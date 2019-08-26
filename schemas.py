import marshmallow as ma
from marshmallow.exceptions import ValidationError


class TransactionSchema(ma.Schema):

    class Meta:
        strict = True
        ordered = True

    _id = ma.fields.UUID(dump_only=True)
    transactions_id = ma.fields.Int()
    bonus_card_id = ma.fields.Int()
    bonus_miles = ma.fields.Int()
    flight_from = ma.fields.String()
    flight_to = ma.fields.String()
    flight_date = ma.fields.String()

    @ma.validates('flight_date')
    def validate_flight_date(self, value):
        try:
            value = ma.utils.from_iso_date(value)
        except ValueError:
            raise ValidationError('flight_date must be a date in "%Y-%m-%d" format')

    @ma.post_load(pass_many=False)
    def check_flight_from_and_flight_to(self, data, **kwargs):
        if data['flight_from'] == data['flight_to']:
            raise ValidationError(
                'Fields "flight_from" and "flight_to" can not have the same value'
            )
        return data


class UserSchema(ma.Schema):

    _id = ma.fields.UUID(dump_only=True)
    name = ma.fields.String()
    email = ma.fields.String()
    bonus_card_id = ma.fields.Int()
