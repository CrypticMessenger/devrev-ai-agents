from constants import EXAMPLE_TEMPLATE, all_tools
from openai import OpenAI
from tools import create_description,create_description_with_example
from add_embedding import add_embedding
from get_embedding import search_similar
from update_embedding import update_embedding

class OpenAIWrapper:
  def __init__(self,client,text_model="gpt-3.5-turbo-1106",embedding_model="text-embedding-ada-002",example_template = ""):
    self.client = client
    self.text_model = text_model
    self.embedding_model = embedding_model
    self.example_template = example_template

  def generate_examples(self,function_description,number_of_examples=3):
    updated_ex_template = self.example_template.format(number_of_examples=number_of_examples)
    response = self.client.chat.completions.create(
    model=self.text_model,
    messages=[
      {"role": "system", "content": updated_ex_template},
      {"role": "user", "content": function_description}
    ]
  )
    return response.choices[0].message.content
  
  def get_embedding(self,text):
    text = text.replace("\n", " ")
    return self.client.embeddings.create(input = [text], model=self.embedding_model).data[0].embedding
  
  def add_functionDB(self,function_name,function_description):
    # implmeent logic of insertion
    embedding = self.get_embedding(function_description)
    data = {
      'name':function_name,
      'model':'openai',
      'description':function_description,
      'embedding':embedding
    }

    response = add_embedding(data)

    return response
  
  def update_functionDB(self,function_name,function_description,embedding):
    ## implement logic of updation
    embedding = self.get_embedding(function_description)
    data = {
      'name':function_name,
      'model':'openai',
      'description':function_description,
      'embedding':embedding
    }

    response = update_embedding(data)

    return response
  
  def get_related_tools(self,query):
    #implement logic of getting tools
    embedding = self.get_embedding(query)

    data = {
      'model':'openai',
      'embedding':embedding
    }

    result = search_similar(data)
    return result


if __name__=="__main__":
  client = OpenAI(api_key = "your-api-key")
  model = OpenAIWrapper(client,example_template=EXAMPLE_TEMPLATE)
  tool = all_tools['tools'][0]
  function_description = create_description(tool)
  examples = model.generate_examples(function_description=function_description,number_of_examples=3)
  function_description = create_description_with_example(function_description,examples)
  model.add_functionDB(tool['name'],function_description) #check
  # query = "what are my work list?"
  query = "Prioritize my P0 issues and add them to the current sprint."
  related_tools = model.get_related_tools(query)
  print("Related tools for query are: ",related_tools)
