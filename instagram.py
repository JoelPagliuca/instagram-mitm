from mitmproxy import ctx
from mitmproxy import command
import re
import json
import csv
from datetime import datetime

class InstagramAddon:
  
  accounts = {}
  media = {}

  def response(self, flow):
    url = flow.request.url
    if "https://www.instagram.com/api/v1/users/web_profile_info/" in url:
      ctx.log.info("[+] " + url)
      account_name = flow.request.query["username"]
      response_content = flow.response.content.decode("utf-8")
      json_data = json.loads(response_content)
      user_data = json_data["data"]["user"]
      self.accounts[account_name] = {
        "account_name": account_name,
        "follower_count": user_data["edge_followed_by"]["count"],
        "following_count": user_data["edge_follow"]["count"],
        "id": user_data["id"]
      }
    elif "https://www.instagram.com/api/v1/feed/user/" in url:
      flow.response.content = flow.response.content.replace(
        b'"auto_load_more_enabled":false', b'"auto_load_more_enabled":true'
      )
      ctx.log.info("[+] " + url)
      response_content = flow.response.content.decode("utf-8")
      json_data = json.loads(response_content)
      userId = ""
      if "username" in url:
        username = re.search(r"/user/(\w+)/username", url).group(1)
        userId = json_data["user"]["pk"]
      else:
        userId = re.search(r"/user/(\d+)/", url).group(1)
      if userId not in self.media:
        self.media[userId] = []
      for item in json_data["items"]:
        if any(i["id"] == item["id"] for i in self.media[userId]):
          continue
        data = {
          "id": item["id"],
          "like_count": item["like_count"],
          "comment_count": item["comment_count"],
          # "caption": item["caption"]["text"].replace(",", ""),
          # "accessibility_caption": item["accessibility_caption"].replace(",", "") if "accessibility_caption" in item else "-",
          "taken_at": item["taken_at"],
        }
        try:
          post_date = datetime.fromtimestamp(int(item["taken_at"]))
          data["year_taken"] = post_date.year
          data["month_taken"] = post_date.month
          data["day_taken"] = post_date.day
          data["week_number"] = post_date.isocalendar()[1]
        except:
          pass

        self.media[userId].append(data)
  
  @command.command("instadump")
  def instadump(self):
    ctx.log.warn(self.accounts)
    ctx.log.warn(self.media)
    for accountname, user in self.accounts.items():
      posts = self.media[user["id"]]
      if len(posts) == 0:
        continue
      keys = posts[0].keys()
      with open(accountname+".csv", 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(posts)
    keys = list(self.accounts.values())[0]
    accounts = self.accounts.values()
    with open("accounts.csv", 'w', newline='') as output_file:
      dict_writer = csv.DictWriter(output_file, keys)
      dict_writer.writeheader()
      dict_writer.writerows(accounts)

addons = [
  InstagramAddon()
]
