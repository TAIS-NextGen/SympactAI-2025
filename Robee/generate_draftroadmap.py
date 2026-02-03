if __name__ == "__main__":
    from MilestonesGeneration.utils.filter import filter_info
    from MilestonesGeneration.utils.career_summary import main_CS
    from MilestonesGeneration.utils.get_target_format import main
    filter_info(scrape = False) # scrape the links given in the txt files
    main_CS()
    main()
    print("Milestones generation completed successfully.")
    print("Causality analysis will be performed next.")
    from custom_causality import main as causality_main
    causality_main()
    print("Causality analysis completed successfully.")
    print("All processes completed successfully.")

