def convert_results_format(
    results: dict[str, dict[tuple, float]]
) -> dict[str, dict[str, float]]:
    converted_results = {}
    for outer_key, inner_dict in results.items():
        converted_inner_dict = {
            " | ".join(key): value for key, value in inner_dict.items()
        }
        converted_results[outer_key] = converted_inner_dict
    return converted_results
