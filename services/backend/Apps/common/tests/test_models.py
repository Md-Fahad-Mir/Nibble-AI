import uuid
from unittest import mock

from django.db import models
from django.test import TestCase

from Apps.common.models import AuditLog, BaseModel, SoftDeleteModel


class AuditLogTests(TestCase):
    def test_uuid_primary_key_and_timestamps(self):
        log = AuditLog.objects.create(
            action=AuditLog.Action.LOGIN,
            actor_type="user",
            actor_id="123",
        )
        self.assertIsInstance(log.id, uuid.UUID)
        self.assertIsNotNone(log.created_at)
        self.assertIsNotNone(log.updated_at)

    def test_metadata_defaults_to_empty_dict(self):
        log = AuditLog.objects.create(action=AuditLog.Action.OTHER)
        self.assertEqual(log.metadata, {})


# A throwaway concrete model so we can exercise the SoftDeleteModel mixin.
# It has no DB table/migration, so tests stub out save() to stay in-memory.
class SoftDeletableForTests(BaseModel, SoftDeleteModel):
    name = models.CharField(max_length=50)

    class Meta:
        app_label = "common"


class SoftDeleteModelTests(TestCase):
    """Verifies soft-delete semantics without persisting (no migration needed)."""

    def test_delete_sets_flags_instead_of_removing(self):
        obj = SoftDeletableForTests(name="x")
        with mock.patch.object(SoftDeletableForTests, "save", autospec=True):
            obj.delete()
        self.assertTrue(obj.is_deleted)
        self.assertIsNotNone(obj.deleted_at)

    def test_restore_clears_flags(self):
        obj = SoftDeletableForTests(name="x")
        with mock.patch.object(SoftDeletableForTests, "save", autospec=True):
            obj.delete()
            obj.restore()
        self.assertFalse(obj.is_deleted)
        self.assertIsNone(obj.deleted_at)
