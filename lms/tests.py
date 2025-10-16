from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from lms.models import Course, Lesson, Subscription

User = get_user_model()


class LessonAndSubscriptionTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # пользователи
        cls.owner = User.objects.create_user(
            email="owner@example.com", password="pw123456"
        )
        cls.other = User.objects.create_user(
            email="other@example.com", password="pw123456"
        )

        # модератор
        cls.moder = User.objects.create_user(
            email="moder@example.com", password="pw123456"
        )
        group, _ = Group.objects.get_or_create(name="moderators")
        cls.moder.groups.add(group)

        # курсы
        cls.my_course = Course.objects.create(
            name="Мой курс", description="", owner=cls.owner
        )
        cls.other_course = Course.objects.create(
            name="Чужой курс", description="", owner=cls.other
        )

        # уроки
        cls.my_lesson = Lesson.objects.create(
            name="Мой урок",
            description="",
            video_url="https://youtu.be/abc123",
            course=cls.my_course,
            owner=cls.owner,
        )
        cls.others_lesson = Lesson.objects.create(
            name="Чужой урок",
            description="",
            video_url="https://youtu.be/zzz999",
            course=cls.other_course,
            owner=cls.other,
        )

    def lessons_list_url(self):
        return reverse("lms:lesson-list")

    def lesson_detail_url(self, pk: int):
        return reverse("lms:lesson-retrieve", kwargs={"pk": pk})

    def lesson_create_url(self):
        return reverse("lms:lesson-create")

    def lesson_update_url(self, pk: int):
        return reverse("lms:lesson-update", kwargs={"pk": pk})

    def lesson_delete_url(self, pk: int):
        return reverse("lms:lesson-delete", kwargs={"pk": pk})

    def course_subscribe_url(self, course_id: int):
        return reverse("lms:course-subscribe", kwargs={"pk": course_id})

    def course_my_subs_url(self):
        return reverse("lms:course-my-subscriptions")

    # LESSONS

    def _items(self, res):
        return (
            res.data["results"]
            if isinstance(res.data, dict) and "results" in res.data
            else res.data
        )

    def test_lessons_list_owner_sees_only_own(self):
        self.client.force_authenticate(self.owner)
        res = self.client.get(self.lessons_list_url(), {"page_size": 99})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        items = self._items(res)
        ids = {item["id"] for item in items}
        self.assertIn(self.my_lesson.id, ids)
        self.assertNotIn(self.others_lesson.id, ids)

    def test_lessons_list_moderator_sees_all(self):
        self.client.force_authenticate(self.moder)
        res = self.client.get(self.lessons_list_url(), {"page_size": 99})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        items = self._items(res)
        ids = {item["id"] for item in items}
        self.assertIn(self.my_lesson.id, ids)
        self.assertIn(self.others_lesson.id, ids)

    def test_owner_can_create_lesson_in_own_course(self):
        self.client.force_authenticate(self.owner)
        payload = {
            "name": "Новый урок",
            "description": "",
            "video_url": "https://www.youtube.com/watch?v=abcd",
            "course": self.my_course.id,
        }
        res = self.client.post(self.lesson_create_url(), payload, format="json")
        self.assertIn(res.status_code, (status.HTTP_201_CREATED, status.HTTP_200_OK))
        self.assertTrue(
            Lesson.objects.filter(name="Новый урок", course=self.my_course).exists()
        )

    def test_owner_cannot_create_lesson_in_foreign_course(self):
        self.client.force_authenticate(self.owner)
        payload = {
            "name": "Чужой урок",
            "description": "",
            "video_url": "https://youtu.be/abcd",
            "course": self.other_course.id,
        }
        res = self.client.post(self.lesson_create_url(), payload, format="json")
        self.assertIn(
            res.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_400_BAD_REQUEST)
        )

    def test_moderator_cannot_create_or_delete_lesson(self):
        self.client.force_authenticate(self.moder)
        # создать
        payload = {
            "name": "Модераторский урок",
            "description": "",
            "video_url": "https://youtu.be/abcd",
            "course": self.my_course.id,
        }
        res = self.client.post(self.lesson_create_url(), payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        res2 = self.client.delete(self.lesson_delete_url(self.my_lesson.id))
        self.assertEqual(res2.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_update_and_delete_own_lesson(self):
        self.client.force_authenticate(self.owner)

        res_upd = self.client.patch(
            self.lesson_update_url(self.my_lesson.id),
            {"name": "Переименован"},
            format="json",
        )
        self.assertIn(
            res_upd.status_code, (status.HTTP_200_OK, status.HTTP_202_ACCEPTED)
        )
        self.my_lesson.refresh_from_db()
        self.assertEqual(self.my_lesson.name, "Переименован")

        res_del = self.client.delete(self.lesson_delete_url(self.my_lesson.id))
        self.assertEqual(res_del.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(id=self.my_lesson.id).exists())

    def test_other_user_cannot_update_or_delete_foreign_lesson(self):
        self.client.force_authenticate(self.other)
        res_upd = self.client.patch(
            self.lesson_update_url(self.my_lesson.id), {"name": "Хак"}, format="json"
        )
        self.assertEqual(res_upd.status_code, status.HTTP_403_FORBIDDEN)
        res_del = self.client.delete(self.lesson_delete_url(self.my_lesson.id))
        self.assertEqual(res_del.status_code, status.HTTP_403_FORBIDDEN)

    def test_video_url_validator_blocks_non_youtube(self):
        self.client.force_authenticate(self.owner)
        payload = {
            "name": "Wrong video host",
            "description": "",
            "video_url": "https://vimeo.com/123",
            "course": self.my_course.id,
        }
        res = self.client.post(self.lesson_create_url(), payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("video_url", res.data)

    # SUBSCRIPTIONS

    def test_subscribe_unsubscribe_flow(self):
        self.client.force_authenticate(self.owner)

        res_sub = self.client.post(self.course_subscribe_url(self.other_course.id))
        self.assertIn(
            res_sub.status_code, (status.HTTP_200_OK, status.HTTP_201_CREATED)
        )
        self.assertTrue(
            Subscription.objects.filter(
                user=self.owner, course=self.other_course
            ).exists()
        )

        res_sub2 = self.client.post(self.course_subscribe_url(self.other_course.id))
        self.assertEqual(res_sub2.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Subscription.objects.filter(
                user=self.owner, course=self.other_course
            ).count(),
            1,
        )

        res_list = self.client.get(self.course_my_subs_url())
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)

        def extract_course_id(row):
            c = row.get("course")
            if isinstance(c, dict):
                return c.get("id") or c.get("pk")
            return c

        returned_ids = {extract_course_id(row) for row in res_list.data}
        self.assertIn(self.other_course.id, returned_ids)

        res_unsub = self.client.delete(self.course_subscribe_url(self.other_course.id))
        self.assertEqual(res_unsub.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Subscription.objects.filter(
                user=self.owner, course=self.other_course
            ).exists()
        )

    def test_unauthenticated_cannot_use_subscription_endpoints(self):
        self.client.force_authenticate(user=None)
        res = self.client.post(self.course_subscribe_url(self.my_course.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
