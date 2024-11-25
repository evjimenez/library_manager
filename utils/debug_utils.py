def print_query_results(results, table_name="Consulta"):
    """
    Imprime los resultados de una consulta MySQL mostrando índices y valores
    
    Args:
        results: Lista de tuplas resultado de la consulta
        table_name: Nombre identificativo de la consulta/tabla
    """
    if not results:
        print(f"\nNo hay resultados para: {table_name}")
        return
        
    # Tomar el primer resultado para mostrar la estructura
    first_result = results[0]
    
    print(f"\n{'='*20} {table_name} {'='*20}")
    print(f"Estructura de datos ({len(first_result)} columnas):")
    
    # Mostrar cada resultado con sus índices
    for result in results:
        print("\nRegistro:")
        for i, value in enumerate(result):
            print(f"{i}: {value}")
        print("-" * 50)