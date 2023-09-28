from celery.task import task

from books.models import Loan


@task()
def revoke_expired_loans_task():
    """
    Terminate expired all expired loans on system.
    This fires LOAN_EXPIRED signal with every terminated loan,
    which publishes a graphene subscription over websockets.
    """

    active = Loan.objects.active()
    counts = dict(
        leases_active=0, leases_expired=0,
        loans_active=0, loans_expired=0,
    )

    for loan in active:
        lease_counts = loan.expire_ended()
        counts['leases_active'] += lease_counts['active']
        counts['leases_expired'] += lease_counts['expired']

    msg = "Expired {leases_expired}/{leases_active} leases on {loans_active}/{loans_expired} loans"
    print("-- %s -- " % msg.format(**counts))
