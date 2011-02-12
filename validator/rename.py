import imdb, os

ia = imdb.IMDb()

extensions = ['.avi','.mkv']

for name in os.listdir('/stuff/shared/videos/movies-other/'):
	for ext in extensions:
		if name.endswith(ext):
			name = name[:-4]
			results =  ia.search_movie(name, results=5)
			if len(results) < 1:
				"No Results for: %s" % name
			else:
				print "Suggestions for: %s" % name
				for i in xrange(len(results)):
					result = results[i]
					print "%s: %s (%s)" % (i, result['title'], result['year'])
				result = results[int(raw_input("Correct Name Index: "))]
				print "Rename to: %s" % result
