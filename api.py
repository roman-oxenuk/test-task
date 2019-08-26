from flask import request
from flask.views import MethodView
from flask_login import login_required

from schemas import TransactionSchema, UserSchema
from db import mongo


class TransactionsView(MethodView):

    transaction_schema = TransactionSchema(many=True)

    def get_objects(self, page, page_size):
        from flask_login import current_user
        filter_params = {'bonus_card_id': current_user.bonus_card_id}

        offset = page_size * (page - 1)
        objects = [
            obj for obj in
            mongo.db.transactions.find(filter_params).limit(page_size).skip(offset)
        ]
        has_next = bool([
            obj for obj in
            mongo.db.transactions.find(filter_params).limit(1).skip(offset + page_size)
        ])
        total = mongo.db.transactions.count_documents(filter_params)
        return {
            'total': total,
            'count': len(objects),
            'prev': f'{request.path}?page={page-1}' if (objects and offset) else None,
            'next': f'{request.path}?page={page+1}' if (objects and has_next) else None,
            'objects': self.transaction_schema.dump(objects),
        }

    @login_required
    def search(self, *args, **kwargs):
        page = kwargs.pop('page', 1)
        page_size = kwargs.pop('page_size', 10)
        return self.get_objects(page, page_size)

    def post(self, *args, **kwargs):
        request_body = kwargs.pop('body')
        request_body = self.transaction_schema.load(request_body)

        objs_to_create = []
        for new_trans in request_body:
            new_obj = dict(**new_trans)
            objs_to_create.append(new_obj)

        objs_to_create = self.transaction_schema.dump(objs_to_create)
        result = mongo.db.transactions.insert_many(objs_to_create, ordered=True)

        for ind, inserted_id in enumerate(result.inserted_ids):
            objs_to_create[ind]['_id'] = inserted_id

        return self.transaction_schema.dump(objs_to_create), 201


class UserView(MethodView):

    user_schema = UserSchema()

    @login_required
    def search(self):
        from flask_login import current_user
        return self.user_schema.dump(current_user), 200
