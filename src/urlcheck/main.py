import re

import vkquick as vq

from . import config


@vq.Reaction("message_new")
async def urlcheck(
    api: vq.API,
    event: vq.Event(),
    sender: vq.Sender()
):
    """
    Update data for user
    """
    link = re.fullmatch(
        config.LINK_PATTERN, event.object.message.text
    )

    if event.object.message.peer_id > vq.PEER:
        if not re.fullmatch(
            config.LINK_PATTERN, event.object.message.text
        ) and not (
            "action" in event.object.message and
            event.object.message.action.type in (
                "chat_invite_user", "chat_invite_user_by_link"
            )
        ):
            await api.messages.send(
                peer_id=event.object.message.peer_id,
                message=config.INVALID_LINK,
                random_id=0
            )
            await api.messages.remove_chat_user(
                chat_id=event.object.message.peer_id - vq.PEER,
                user_id=sender.id
            )
