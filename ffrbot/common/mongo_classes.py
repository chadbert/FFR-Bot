from typing import *


class GuildConfig(TypedDict):
    id: int
    admin_role_ids: Optional[List[int]]
    polls_category_id: Optional[int]
    role_requests_channel_id: Optional[int]
    race_org_channel_id: Optional[int]
    race_results_channel_id: Optional[int]
