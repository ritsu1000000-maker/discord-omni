from discord_omni import power_tools as p, power_feature_count

print("Power features:", power_feature_count())

print(p.mention_user("123456789012345678"))
print(p.timestamp_relative(1735689600))

url = p.build_bot_invite_url(
    "APPLICATION_ID",
    permissions=p.permission_value("VIEW_CHANNEL", "SEND_MESSAGES"),
)
print(url)

command = p.slash_command(
    "hello",
    "挨拶します",
    options=[
        p.string_option("name", "名前", required=False)
    ],
)
print(command)
