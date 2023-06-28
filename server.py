from flask import Flask, jsonify, request
from flask.views import MethodView
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from models import Session, Advertisement
from schema import CreateAdvertisement, PatchAdvertisement, VALIDATION_CLASS


app = Flask("app")

class HttpError(Exception):

    def __init__(self, status_code: int, message: dict | list | str):
        self.status_code = status_code
        self.message = message

@app.errorhandler(HttpError)
def http_error_handler(error: HttpError):

    error_message = {"status": "error", "description": error.message}
    response = jsonify(error_message)
    response.status_code = error.status_code
    return response

def validate_json(json_data: dict, validation_model: VALIDATION_CLASS):

    try:
        model_object = validation_model(**json_data)
        model_object_dict = model_object.dict(exclude_none=True)
    except ValidationError as err:
        raise HttpError(400, message=err.errors())
    
    return model_object_dict

def get_advertisement(session: Session, advertisement_id: int):

    advertisement = session.get(Advertisement, advertisement_id)

    if advertisement is None:
        raise HttpError(404, message="advertisement doesn't exist")
    
    return advertisement

class AdvertisementView(MethodView):

    def get(self, advertisement_id: int):

        with Session() as session:
            advertisement = get_advertisement(session, advertisement_id)
            return jsonify({
                    "id": advertisement.id,
                    "title": advertisement.title,
                    "description": advertisement.description,
                    "owner": advertisement.owner,
                    "creation_date": advertisement.creation_date.isoformat(timespec='hours')})

    def post(self):

        json_data = validate_json(request.json, CreateAdvertisement)

        with Session() as session:
            advertisement = Advertisement(**json_data)
            session.add(advertisement)

            try:
                session.commit()
            except IntegrityError:
                raise HttpError(409, f'{json_data["title"]} с таким заголовком уже существует')
            
            return jsonify({"id": advertisement.id})

    def patch(self, advertisement_id: int):

        json_data = validate_json(request.json, PatchAdvertisement)

        with Session() as session:

            advertisement = get_advertisement(session, advertisement_id)

            for field, value in json_data.items():
                setattr(advertisement, field, value)

            session.add(advertisement)

            try:
                session.commit()
            except IntegrityError:
                raise HttpError(409, f'{json_data["title"]} с таким заголовком уже существует')
            
            return jsonify({
                    "id": advertisement.id,
                    "title": advertisement.title,
                    "description": advertisement.description,
                    "owner": advertisement.owner,
                    "creation_date": advertisement.creation_date.isoformat(timespec='hours')})

    def delete(self, advertisement_id: int):

        with Session() as session:

            advertisement = get_advertisement(session, advertisement_id)
            session.delete(advertisement)
            session.commit()

            return jsonify({"status": "successfully"})

app.add_url_rule(
    "/advertisement/<int:advertisement_id>",
    view_func=AdvertisementView.as_view("with_advertisement_id"),
    methods=["GET", "PATCH", "DELETE"],)

app.add_url_rule("/advertisement/", view_func=AdvertisementView.as_view("create_advertisement"), methods=["POST"])


if __name__ == "__main__":
    app.run()