from typing import MutableSequence

from rest_framework.authtoken.models import Token


def get_user_id_by_token(token: str) -> int:
    token_obj = Token.objects.get(key=token)
    user_id = token_obj.user_id

    return user_id


def ids_to_str(ids: MutableSequence[int],
               ) -> str:
    string = ' '.join(str(id) for id in ids)
    return string


def str_to_ids(string: str,
               ) -> list[int]:
    ids = [int(id) for id in string.split()]
    return ids


def check_user_is_admin(user_id: int,
                        ) -> None:
    pass
