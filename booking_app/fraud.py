from datetime import timedelta

from django.utils import timezone

from .models import Booking, FraudAnomalyFlag, Review

PHOTO_REJECTED_RISK = 40
FAKE_REVIEWS_RISK = 35
TOO_MANY_CANCELS_RISK = 30
BAD_RATINGS_RISK = 30
DAYS_TO_CHECK = 30


def create_flag(user, anomaly_type, risk_score, description, booking=None):
    already_open = FraudAnomalyFlag.objects.filter(
        user=user, anomaly_type=anomaly_type, flag_status=FraudAnomalyFlag.OPEN
    ).exists()
    if not already_open:
        FraudAnomalyFlag.objects.create(
            user=user,
            booking=booking,
            anomaly_type=anomaly_type,
            risk_score=risk_score,
            description=description,
        )


def check_rejected_photo(booking):
    customer_name = booking.customer.user.username
    description = f'{customer_name} rejected the completion photo for "{booking.service.title}".'
    create_flag(booking.worker.user, FraudAnomalyFlag.DISPUTED_COMPLETION, PHOTO_REJECTED_RISK,
                description, booking)


def check_cancels(customer):
    since = timezone.localdate() - timedelta(days=DAYS_TO_CHECK)
    cancels = customer.bookings.filter(status=Booking.CANCELLED, booking_date__gte=since).count()
    if cancels >= 3:
        description = f'{cancels} cancelled bookings in the last {DAYS_TO_CHECK} days.'
        create_flag(customer.user, FraudAnomalyFlag.EXCESSIVE_CANCELLATION, TOO_MANY_CANCELS_RISK,
                    description)


def check_bad_ratings(worker):
    since = timezone.now() - timedelta(days=DAYS_TO_CHECK)
    one_star_count = worker.reviews.filter(rating=1, created_date__gte=since).count()
    if one_star_count >= 3:
        description = f'{one_star_count} one-star reviews in the last {DAYS_TO_CHECK} days.'
        create_flag(worker.user, FraudAnomalyFlag.LOW_RATING_PATTERN, BAD_RATINGS_RISK, description)


def check_fake_reviews(review):
    since = timezone.now() - timedelta(days=DAYS_TO_CHECK)
    five_star_count = Review.objects.filter(
        customer=review.customer, worker=review.worker, rating=5, created_date__gte=since
    ).count()
    if five_star_count >= 3:
        customer_name = review.customer.user.username
        description = f'{customer_name} gave this worker 5 stars {five_star_count} times in the last {DAYS_TO_CHECK} days.'
        create_flag(review.worker.user, FraudAnomalyFlag.POSSIBLE_FAKE_REVIEWS, FAKE_REVIEWS_RISK,
                    description, review.booking)
