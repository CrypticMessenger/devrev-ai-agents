from constants import PALM_EXAMPLES_TEMPLATES, all_tools, PALM_CONTEXT
from .tools import create_description,create_description_with_example
from .add_embedding import add_embedding, create_index_if_not_exists
from .get_embedding import search_similar
from .update_embedding import update_embedding
import google.generativeai as palm
from .connectdb import connectdb, disconnectdb

class PalmWrapper:
  def __init__(self,client,text_model="models/text-bison@001",embedding_model="models/embedding-gecko-001",example_template = "", palm_context = ""):
    self.client = client
    self.text_model = text_model
    self.embedding_model = embedding_model
    self.example_template = example_template
    self.palm_context = palm_context

  def generate_examples(self,function_description,number_of_examples=3):
    self.example_template[0] = (self.example_template[0][0], self.example_template[0][1].format(number_of_examples=number_of_examples))
    updated_ex_template = self.example_template
    response = self.client.chat(
      context = self.palm_context,
      examples=updated_ex_template,
      messages=function_description,
    )
    return response.last
  
  def get_embedding(self,text):
    text = text.replace("\n", " ")
    return self.client.generate_embeddings(text = text, model=self.embedding_model)['embedding']
  
  def add_functionDB(self,function_name,function_description, function_examples, function_arguments):
    # check if the function_exists or not
    collection = connectdb('palm') # connect to db
    
    create_index_if_not_exists(collection, model='palm') # create index if it does not exist

    collection.load() #load collection 

    boolean_expr = f'function_name=="{function_name}"'
    res = collection.query( # query over the collection
      expr = boolean_expr,
      output_fields = ['function_name', 'description', 'embedding', 'examples','arguments'],
      limit=1
    )

    collection.release()
    # if function alreadys exists in the db, simply return that
    if len(res) != 0:
      return res
    
    disconnectdb() # disconnect from the db

    # implmeent logic of insertion
    embedding = self.get_embedding(function_description)
    data = {
      'function_name':function_name,
      'description':function_description,
      'embedding':embedding,
      'examples':function_examples,
      'arguments': function_arguments
    }

    response = add_embedding(data, model='palm')

    return response
  
  def update_functionDB(self,function_name,function_description,embedding, function_examples, function_arguments):
    # implement logic of updation
    embedding = self.get_embedding(function_description)
    data = {
        'function_name':function_name,
        'description':function_description,
        'embedding':embedding,
        'examples':function_examples,
        'arguments':function_arguments
    }

    response = update_embedding(data)

    return response

  def get_related_tools(self,query):
    #implement logic of getting tools
    embedding = self.get_embedding(query)

    result = search_similar(embedding, model='palm')
    return result


if __name__=="__main__":
    palm.configure(api_key="api-key-using-console-google")
    model = PalmWrapper(palm,example_template=PALM_EXAMPLES_TEMPLATES, palm_context = PALM_CONTEXT)
    # tool = all_tools['tools'][0]
    # function_description = create_description(tool)
    # examples = model.generate_examples(function_description=function_description,number_of_examples=3)
    # function_description = create_description_with_example(function_description,examples)
    # model.add_functionDB(tool['name'],function_description) #check
    # query = "what are my work list?"
    # query = "Prioritize my P0 issues and add them to the current sprint."
    # related_tools = model.get_related_tools(query)
    # print("Related tools for query are: ",related_tools)

    # a = model.get_embedding('works_list')
    # print(a)


    # embedding = data['works_list'] 
    # dic = {'function_name':'works_list',
    #       'description':'works_list',
    #       'embedding':embedding,
    #       'examples':'examples'}
    # model.add_functionDB('works_list', 'description', 'example', [{'arg':'v0'}])
    # print(examples)
    a = model.get_related_tools('what are my work list')
    print(a)

