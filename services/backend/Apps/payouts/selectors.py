"""Read-side queries for payouts."""

from Apps.payouts.models import PayoutBatch, PayoutMethod, WithdrawalRequest


def methods_for_user(user):
    return PayoutMethod.objects.filter(user=user)


def withdrawals_for_user(user):
    return WithdrawalRequest.objects.filter(user=user).select_related("payout_method")


def get_user_withdrawal(user, withdrawal_id) -> WithdrawalRequest | None:
    return WithdrawalRequest.objects.filter(user=user, id=withdrawal_id).first()


def all_withdrawals(*, status: str = ""):
    qs = WithdrawalRequest.objects.select_related("user", "payout_method").all()
    if status:
        qs = qs.filter(status=status)
    return qs


def get_withdrawal(withdrawal_id) -> WithdrawalRequest | None:
    return WithdrawalRequest.objects.filter(id=withdrawal_id).first()


def all_batches():
    return PayoutBatch.objects.all()


def get_batch(batch_id) -> PayoutBatch | None:
    return PayoutBatch.objects.filter(id=batch_id).first()
