from flask import Flask, request, jsonify
import awsgi
import requests

app = Flask(__name__)

# Define the base URL of the external API
base_url = "https://app.ylytic.com/ylytic/test"

months = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12",
}

@app.route("/",methods=["GET"])
def index():
    response1 = requests.get(base_url)
    comment1 = response1.json()
    return jsonify(comment1)


@app.route("/search", methods=["GET"])
def search_comments():
    try:
        # Extract query parameters from the request
        search_author = request.args.get("search_author")
        dateparts_from = request.args.get("at_from")
        dateparts_to = request.args.get("at_to")
        like_from = request.args.get("like_from")
        like_to = request.args.get("like_to")
        reply_from = request.args.get("reply_from")
        reply_to = request.args.get("reply_to")
        search_text = request.args.get("search_text")

        #converting the dates in parameter in a format eg:yyyymmdd so that it easy to compare
        at_from = dateparts_from
        if dateparts_from:
            parts = dateparts_from.split('-')
            at_from = parts[2]+parts[1]+parts[0]
        at_to = dateparts_to
        if dateparts_to:
            parts = dateparts_to.split('-')
            at_to = parts[2]+parts[1]+parts[0]


        # Make a request to the YouTube comments API
        response = requests.get(base_url)

        # Check if the external API responded with a successful status code (200)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch data from the external API"}), 500

        comments = response.json()
                

        # Filter comments based on search criteria
        filtered_comments = []



        for comment in comments["comments"]:
            #converting the dates before comparing in the format yyyymmdd
            datesplit = comment["at"].split()
            publishdate = datesplit[3]+months[datesplit[2]]+datesplit[1]
             
            if isinstance(comment,dict) and "author" in comment:
                if(
                    (not search_author or search_author.lower() in comment["author"].lower()) and
                    (not at_from or int(publishdate) >= int(at_from)) and
                    (not at_to or int(publishdate) <= int(at_to)) and
                    (not like_from or comment["like"] >= int(like_from)) and
                    (not like_to or comment["like"] <= int(like_to)) and
                    (not reply_from or comment["reply"] >= int(reply_from)) and
                    (not reply_to or comment["reply"] <= int(reply_to)) and
                    (not search_text or search_text.lower() in comment["text"].lower())
                    ):
                    filtered_comments.append(comment)

        return jsonify(filtered_comments)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

def lambda_handler(event,context):
    return awsgi.response(app, event, context, base64_content_types={"image/png"})

if __name__ == "__main__":
    app.run(debug=True)


