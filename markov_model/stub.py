from suggestion_model import Suggestion_Generator

if __name__ == '__main__':
	
	#stub code just to test out the class
	model = Suggestion_Generator()
	model.train('sample_conversations.json')
	model.dump_to_pickle()
	# model.print_corpus(model.preprocessed_corpus, True, True)

	#this takes a substantial amount of clocktime
	