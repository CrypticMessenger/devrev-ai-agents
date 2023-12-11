from pymilvus import DataType, FieldSchema, CollectionSchema

dim_openai = 1536
dim_bert = 768
dim_palm = 768

# -------------------------------------------------------
# function name
func_id_field = FieldSchema(name="function_name", dtype=DataType.VARCHAR, max_length=256, is_primary=True, description="func_name")
# function model
model_name_field = FieldSchema(name="model_name", dtype=DataType.VARCHAR, max_length=256, description="model name")
# embedding based on model
openai_embedding_field = FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, description="embeddings", dim=dim_openai)
bert_embedding_field = FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, description="embeddings", dim=dim_bert)
palm_embedding_field = FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, description="embeddings", dim=dim_palm)
# description of function/tool
func_desc_field = FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=2000, description="func_desc")
# examples of tool
func_example_field = FieldSchema(name="examples", dtype=DataType.VARCHAR, max_length=4000, description="func_examples")
# arguments that the tool has
func_arg_field = FieldSchema(name="arguments", dtype=DataType.JSON, description="func_arguments")

# define schemas
schema_openai = CollectionSchema(fields=[func_id_field, model_name_field,func_desc_field, openai_embedding_field,func_example_field, func_arg_field], auto_id=False, description="embeddings for different models schema")

schema_bert = CollectionSchema(fields=[func_id_field,model_name_field,func_desc_field, bert_embedding_field,func_example_field, func_arg_field], auto_id=False, description="embeddings for different models schema")

schema_palm = CollectionSchema(fields=[func_id_field, model_name_field, func_desc_field, palm_embedding_field,func_example_field, func_arg_field], auto_id=False, description="embeddings for different models schema")
# ---------------------------------------------------------
