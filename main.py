from website import create_app

app = create_app()
# db = getConnection()

if __name__ == '__main__':
	# debug更改code會自動更改網頁
	app.run(debug=True)