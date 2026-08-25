import os
from discord_omni.community import TopGGClient

topgg = TopGGClient(os.environ["TOPGG_TOKEN"])

project = topgg.get_project()
print(project["name"])

# topgg.post_metrics(server_count=100, shard_count=1)
