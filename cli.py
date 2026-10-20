import duckdb

db = duckdb.connect("db.duckdb")

def get_next_user_id():
	row = db.execute("select max(UserID) from User").fetchone()
	return 1 if row[0] is None else row[0] + 1

# ------------------------------------------
# ------------------------------------------ Second Capability, as shown in our video
# ------------------------------------------

def search_media():
	media_type = input("media type (visual | written | game): ").strip()
	

	if media_type == "visual":
		name = input("media name: ").strip()
		rows = db.execute(" select m.MediaID, m.Title, m.ReleaseDate, m.Genre, vm.TotalRunTime, vm.EpisodeCount, vm.Studio, vm.Director, vm.Producer from Media m natural join VisualMedia vm where lower(Title) like lower(?)", (f"%{name}%",)).fetchall()

		print("\n--- Visual Media ---")
		for r in rows:
			print(f"ID: {r[0]}")
			print(f"Title: {r[1]}")
			print(f"Release Date: {r[2]}")
			print(f"Genre: {r[3]}")
			print(f"Runtime: {r[4]}")
			print(f"Episodes: {r[5]}")
			print(f"Studio: {r[6]}")
			print(f"Director: {r[7]}")
			print(f"Producer: {r[8]}\n")

	elif media_type == "written":
		name = input("media name: ").strip()
		rows = db.execute("select m.MediaID, m.Title, m.ReleaseDate, m.Genre, wm.Chapters, wm.Volumes, wm.Author, wm.Demographic, wm.Series from Media m natural join WrittenMedia wm where lower(Title) like lower(?)""", (f"%{name}%",)).fetchall()

		print("\n--- Written Media ---")
		for r in rows:
			print(f"ID: {r[0]}")
			print(f"Title: {r[1]}")
			print(f"Release Date: {r[2]}")
			print(f"Genre: {r[3]}")
			print(f"Chapters: {r[4]}")
			print(f"Volumes: {r[5]}")
			print(f"Author: {r[6]}")
			print(f"Demographic: {r[7]}")
			print(f"Series: {r[8]}\n")

	elif media_type == "game":
		name = input("media name: ").strip()
		rows = db.execute("select m.MediaID, m.Title, m.ReleaseDate, m.Genre, g.Developer, g.Publisher, g.Platform from Media m natural join VideoGame g where lower(Title) like lower(?)", (f"%{name}%",)).fetchall()

		print("\n--- Video Games ---")
		for r in rows:
			print(f"ID: {r[0]}")
			print(f"Title: {r[1]}")
			print(f"Release Date: {r[2]}")
			print(f"Genre: {r[3]}")
			print(f"Developer: {r[4]}")
			print(f"Publisher: {r[5]}")
			print(f"Platform: {r[6]}\n")

	else:
		print("Invalid media type.")
		return

	if not rows:
		print("No results found.")

# ------------------------------------------
# ------------------------------------------ Third Capability, as shown in our video
# ------------------------------------------

def analytics():
	media_type = input("media type (visual | written | game): ").strip()

	if media_type == "visual":
		table = "VisualMedia"
		attributes = ["Studio", "Director", "Producer", "EpisodeCount"]
	elif media_type == "written":
		table = "WrittenMedia"
		attributes = ["Author", "Demographic", "Series", "Volumes"]
	elif media_type == "game":
		table = "VideoGame"
		attributes = ["Developer", "Publisher", "Platform"]
	else:
		print("Error. Invalid media type.")
		return

	print("available attributes (Requires correct capitalization):")
	for attr in attributes:
		print(f"- {attr}")

	attribute = input("Attribute: ").strip()
	if attribute not in attributes:
		print("Error. Invalid attribute.")
		return

	value = input(f"Search value for {attribute}: " ).strip()

	query = f"select m.Title, m.ReleaseDate, m.Genre, t.{attribute} from Media m natural join {table} t where lower(t.{attribute}) like lower(?)"

	rows = db.execute(query, (f"%{value}%",)).fetchall()

	if not rows:
		print("No results found.")
		return

	print("\n--- Results ---")
	for r in rows:
		print(f"Title: {r[0]}")
		print(f"Release Date: {r[1]}")
		print(f"Genre: {r[2]}")
		print(f"{attribute}: {r[3]}\n")

# ------------------------------------------
# ------------------------------------------ First Capability, as shown in our video
# ------------------------------------------

def add_media():
	username = input("Username: ").strip()

	user = db.execute("select UserID from User where Username = ?", (username,)).fetchone()
	if not user:
		print("Error. User not found.")
		return

	title = input("Media Title: ").strip()

	media = db.execute("select MediaID from Media where lower(Title) like lower(?)", (title,)).fetchall()
	if not media:
		print("Error. Media not found.")
		return

	if len(media) > 1:
		print("Multiple media found:")
		for m in media:
			print(f"{m[0]}: {m[1]}")

		media_id = input("Select Media ID: ").strip()

		if not any(str(m[0]) == media_id for m in media):
			print("Invalid selection.")
			return

		media_id = int(media_id)
	else:
		media_id = media[0][0]

	rating = input("Rating (1-5): ").strip()
	if not rating.isdigit() or not (1 <= int(rating) <= 5):
		print("Error. Invalid rating.")
		return

	date = input("Date (YYYY-MM-DD): ").strip()
	status = input("Media Status (planned | in-progress | completed): ").strip()

	db.execute("insert into Tracks (UserID, MediaID, Rating, AddDate, MediaStatus) values (?, ?, ?, ?, ?)",
		(user[0], media_id, rating, date, status))

	print("Add successful!")

def update_media():
	username = input("Username: ").strip()

	user = db.execute("select UserID from User where Username = ?", (username,)).fetchone()
	if not user:
		print("Error. User not found.")
		return

	title = input("Media Title: ").strip()

	media = db.execute("select MediaID, Title from Media where lower(Title) like lower(?)", (f"%{title}%",)).fetchall()
	if not media:
		print("Error. Media not found.")

	if len(media) > 1:
		print("Multiple media found:")
		for m in media:
			print(f"{m[0]}: {m[1]}")

		media_id = input("Select Media ID: ").strip()

		if not any(str(m[0]) == media_id for m in media):
			print("Invalid selection.")
			return

		media_id = int(media_id)
	else:
		media_id = media[0][0]

	exists = db.execute("select 1 from Tracks where UserID = ? and MediaID = ?", (user[0], media_id)).fetchone()

	if not exists:
		print("Error. Media not found in user list.")
		return

	rating = input("New Rating (1-5): ").strip()

	if not rating.isdigit() or not (1 <= int(rating) <= 5):
		print("Error. Invalid rating.")
		return

	status = input("New Status (planned | in-progress | completed): ")

	db.execute("update Tracks set Rating = ?, MediaStatus = ? where UserID = ? and MediaID = ?", (rating, status, user[0], media_id))

	print("Update successful!")

def remove_media():
	username = input("Username: ").strip()

	user = db.execute("select UserID from User where Username = ?", (username,)).fetchone()
	if not user:
		print("Error. User not found.")
		return

	title = input("Media Title: ").strip()

	media = db.execute("select MediaID from Media where lower(Title) like lower(?)", (f"%{title}%",)).fetchall()
	if not media:
		print("Error. Media not found.")
		return

	if len(media) > 1:
		print("Multiple media found:")
		for m in media:
			print(f"{m[0]}: {m[1]}")

		media_id = input("Select Media ID: ").strip()

		if not any(str(m[0]) == media_id for m in media):
			print("Invalid selection.")
			return

		media_id = int(media_id)
	else:
		media_id = media[0][0]

	exists = db.execute("select 1 from Tracks where UserID = ? and MediaID = ?", (user[0], media_id)).fetchone()
	if not exists:
		print("Error. Media not found in user list.")
		return

	db.execute("delete from Tracks where UserId = ? and MediaID = ?", (user[0], media_id))

	print("Remove successful!")

def list_media():
	username = input("Username: ").strip()

	rows = db.execute("select t.MediaID, t.Rating, t.AddDate, t.MediaStatus from Tracks t natural join User u where u.Username = ?", (username,)).fetchall()

	if not rows:
		print("No tracked media.")
		return

	print("\n--- Tracked Media ---")
	for r in rows:
		media_id = r[0]

		media_name = db.execute("select Title from Media where MediaID = ?", (media_id,)).fetchone()
		media_type = ""

		if db.execute("select 1 from VisualMedia where MediaID = ?", (media_id,)).fetchone():
			media_type = "visual"
		elif db.execute("select 1 from WrittenMedia where MediaID = ?", (media_id,)).fetchone():
			media_type = "written"
		if db.execute("select 1 from VideoGame where MediaID = ?", (media_id,)).fetchone():
			media_type = "game"

		print(f"Media ID: {media_id}")
		print(f"Title: {media_name[0]}")
		print(f"Type: {media_type}")
		print(f"Rating: {r[1]}")
		print(f"Date Added: {r[2]}")
		print(f"Status: {r[3]}\n")

def login():
	username = input("username: ").strip()
	
	user = db.execute("select UserID from User where Username = ?", (username,)).fetchone()
	if user:
		print("User already exists. Logged In.")
		return

	email = input("email: ").strip()

	user_id = get_next_user_id()

	db.execute("insert into User (UserID, Username, Email, JoinDate) values (?, ?, ?, CURRENT_DATE)", (user_id, username, email))

	print("User created successfully!")

def delete():
	print("WARNING: this function deletes all information related to the user, including tracked media.")

	username = input("username: ").strip()

	user = db.execute("select UserID from User where Username = ?", (username,)).fetchone()
	if not user:
		print ("User not found.")
		return

	user_id = user[0]

	db.execute("delete from Tracks where UserID = ?", (user_id,))
	db.execute("delete from User where UserID = ?", (user_id,))

	print("User successfully deleted.")


def main():
	print("\nHobby Record Keeper CLI (type 'help' for commands)")
	while True:
		command = input(">> ").strip().lower();

		if command == "search":
			search_media()
		elif command == "analytics":
			analytics()
		elif command == "add":
			add_media()
		elif command == "update":
			update_media()
		elif command == "remove":
			remove_media()
		elif command == "list":
			list_media()
		elif command == "login":
			login()
		elif command == "delete":
			delete()
		elif command in ("exit", "e"):
			break
		elif command == "help":
			print("""
--- Help ---

Available Commands:

search
	Search for media by name and type.
	>> search 
	>> media type (written | visual | game): <input>
	>> media name: <input>
	-> Outputs media information that matches type and name.

analytics
	Search for media that share an attribute
	>> analytics
	>> media type (written | visual | game): <input>
	>> available attributes *prints attributes that correspond to media type*: <input>
	>> search value for {attribute}: <input>
	-> Outputs media that share same attribute value.

add
	Add media to a user's tracking list.
	>> add
	>> username: <input>
	>> media name: <input>
	>> *if duplicate names* media id: 
	>> rating: <input>
	>> date: <YYYY-MM-DD>
	>> media status: <planned | in-progress | completed>
	-> Adds entry if user and media exists.

update
	Update media from a user's tracking list.
	>> update
	>> username: <input>
	>> media name: <input>
	>> new rating: <input>
	>> new status: <planned | in-progress | completed>
	-> Updates media using new rating and new status.

remove
	Remove media from a user's tracking list.
	>> remove
	>> username: <input>
	>> media id: <input>
	-> Removes entry if media exist in user's list.

login
	Creates a new user.
	>> username: <input>
	>> email: <input>
	-> Creates a new user if they do not already exist.

delete
	Deletes a user, along with their tracked information.
	>> username:
	-> Deletes user if they exist.

list
	Lists all media tracked by a user.
	>> list
	>> username: <input>
	-> Displays information if user exists.

help
	Displays the help menu.

exit / e
	Exit the program.

--- End ---
			""")
		elif command == "":
			continue
		else:
			print("Unknown command.")

if __name__ == "__main__":
	main()