from pymilvus import DataType, FieldSchema, CollectionSchema

dim_openai = 1536
dim_bert = 768
dim_palm = 768

# -------------------------------------------------------
func_id_field = FieldSchema(name="func_name", dtype=DataType.VARCHAR, max_length=256, is_primary=True, description="func_name")
model_name_field = FieldSchema(name="model_name", dtype=DataType.VARCHAR, max_length=256, description="model name")

openai_embedding_field = FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, description="embeddings", dim=dim_openai)
bert_embedding_field = FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, description="embeddings", dim=dim_bert)
palm_embedding_field = FieldSchema(name="embeddings", dtype=DataType.FLOAT_VECTOR, description="embeddings", dim=dim_palm)

func_desc_field = FieldSchema(name="description", dtype=DataType.VARCHAR, max_length=2000, description="func_desc")

# define schemas
schema_openai = CollectionSchema(fields=[func_id_field, model_name_field,func_desc_field, openai_embedding_field,], auto_id=False, description="embeddings for different models schema")
schema_bert = CollectionSchema(fields=[func_id_field,model_name_field,func_desc_field, bert_embedding_field], auto_id=False, description="embeddings for different models schema")
schema_palm = CollectionSchema(fields=[func_id_field, model_name_field, func_desc_field, palm_embedding_field], auto_id=False, description="embeddings for different models schema")
# ---------------------------------------------------------
