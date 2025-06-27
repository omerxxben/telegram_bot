from Classes.general_tools import pretty_print_df


class Logger:
    def ali_express_log(self,search_query, product_name_english, products_df_detailed,ai_manager, timings,):
        pretty_print_df(products_df_detailed)
        print(f"product name hebrew: {search_query}")
        print(f"product name english: {product_name_english}")
        print("\n" + "=" * 50)
        print("AI USAGE STATISTICS")
        print("=" * 50)
        print(f"Input tokens: {ai_manager.total_tokens_used['prompt_tokens']}")
        print(f"Output tokens: {ai_manager.total_tokens_used['completion_tokens']}")
        print(f"Total runtime of ai: {ai_manager.total_runtime:.3f}s")
        print(f"Total runtime of get products: {timings['get_products']:.3f}s")
        print(f"Total runtime of transform to table: {timings['transform_table']:.3f}s")
        print(f"Total runtime of get details: {timings['get_details']:.3f}s")
        print(f"Total runtime of get image: {timings['get_image']:.3f}s")
        print(f"Total runtime of get short link: {timings['get_short_link']:.3f}s")
        print(f"Total runtime: {timings['total']:.3f}s")
        input_cost = ai_manager.total_tokens_used['prompt_tokens'] * 0.0001 / 1000
        output_cost = ai_manager.total_tokens_used['completion_tokens'] * 0.0004 / 1000
        total_cost = input_cost + output_cost
        print(f"Estimated cost: ${total_cost:.6f}")
        print("=" * 50)
