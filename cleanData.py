for i in stockIds:
    path = get_event_path(i,'finance_report')
    try:
        if os.path.exists(path):
            df = pd.read_csv(path)
            df = index_df_with_time(df,index='reportDate')
    except Exception as e:
        print(path)
        if os.path.exists(path):
            os.remove(path)
