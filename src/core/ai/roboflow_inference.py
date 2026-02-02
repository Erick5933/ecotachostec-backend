from inference_sdk import InferenceHTTPClient

# Crear cliente
client = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="T02OsUf25gIOG7id3A9r"
)

# Ejecutar workflow
result = client.run_workflow(
    workspace_name="frosdh",
    workflow_id="ia-final-uof7b",
    images={
        "image": "mi_imagen.jpg"  # Reemplaza con tu imagen
    },
    use_cache=True
)

# Mostrar resultado
print(result)
