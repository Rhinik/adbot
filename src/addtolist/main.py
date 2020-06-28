import re

import vkquick as vq

from . import config
from src.db import post, get


@vq.Cmd(argline=config.LINK_PATTERN)
@vq.Reaction("message_new")
async def addtolist(screen: vq.Word(), sender: vq.Sender(), event: vq.Event, api: vq.API):
    """
    Handler to command `addtolist`
    """
    info = await api.utils.resolve_screen_name(
        screen_name=screen
    )
    if not info or info.type != "group":
        await api.messages.send(
            peer_id=event.object.message.peer_id,
            message=config.INVALID_LINK,
            random_id=0
        )
        await api.messages.remove_chat_user(
            chat_id=event.object.message.peer_id - vq.PEER,
            user_id=sender.id
        )
        return
    # Последняя позиция пользователя
    last_seq = get(
        """
        SELECT MAX(seq)
        FROM last
        WHERE id = ? AND peer_id = ?;
        """, sender.id, event.object.message.peer_id
    )[0]
    # Максимальная позиция
    max_seq = get(
        """
        SELECT MAX(seq) FROM last WHERE peer_id = ?;
        """, event.object.message.peer_id
    )[0]

    # Если пользователь не писал сообщение
    if last_seq["MAX(seq)"] is None:
        post(
            """
            INSERT INTO last
            (id, peer_id, seq, group_id)
            VALUES
            (?, ?, ?, ?)
            """,
            sender.id,
            event.object.message.peer_id,
            max_seq["MAX(seq)"] + 1 if max_seq["MAX(seq)"] is not None else 1,
            info.object_id
        )
        return


    # Если не прошло DELAY сообщений
    if max_seq["MAX(seq)"] - last_seq["MAX(seq)"] < config.DELAY:
        await api.messages.send(
            peer_id=event.object.message.peer_id,
            message=config.NOT_WAITED,
            random_id=0
        )
        await api.messages.remove_chat_user(
            chat_id=event.object.message.peer_id - vq.PEER,
            user_id=sender.id
        )
        return


    group_ids = get(
        """
        SELECT group_id
        FROM last
        WHERE seq > ? AND seq < ? AND peer_id = ?;
        """,
        last_seq["MAX(seq)"], max_seq["MAX(seq)"] + 1,
        event.object.message.peer_id
    )
    subscribed = 0
    for group in group_ids:
        is_member = await api.groups.is_member(
            group_id=group.group_id,
            user_id=sender.id
        )
        if is_member:
            subscribed += 1

    # Если пользователь не подписался в достаточное количество групп
    if subscribed < config.DELAY:

        await api.messages.send(
            peer_id=event.object.message.peer_id,
            message=config.LOW_SUBSCRIBED,
            random_id=0
        )
        await api.messages.remove_chat_user(
             chat_id=event.object.message.peer_id - vq.PEER,
             user_id=sender.id
        )
        return

    # Все успешно. Обновляем данные в базе
    post(
        """
        INSERT INTO last
        (id, peer_id, seq, group_id)
        VALUES
        (?, ?, ?, ?)
        """,
        sender.id,
        event.object.message.peer_id,
        max_seq["MAX(seq)"] + 1,
        info.object_id
    )
