from langchain import OpenAI, ConversationChain

llm = OpenAI(temperature=0, model_name='gpt-3.5-turbo')
conversation = ConversationChain(llm=llm, verbose=True)

conversation.predict(input="""
    # calculate days between two dates given as string format YYYY-MM-DD
    # leap year feb has 29 days instead of 28
    # Note that start and end day should not be counted and we only care about the absolute difference in dates. 
    # If the order of two dates being compared is flipped the difference remains the same.

    from helpers import return_date_from_str, years_to_days, months_to_days, Date


    def convert_to_days(date:Date)->int:
        years_days = years_to_days(date.year)
        month_days = months_to_days(date.year, date.month)   
        total_days = years_days + month_days + date.day
    
        return total_days

    def days_between_dates(date_1: str, date_2:str):
        date_1_repr = Date(*return_date_from_str(date_1))
        date_2_repr = Date(*return_date_from_str(date_2))
        
        return abs(convert_to_days(date_1_repr) - convert_to_days(date_2_repr)) - 1

    def main(date_1:str, date_2:str)->int:
        days_between = days_between_dates(date_1, date_2)
        
        return days_between

    #TODO: input validation
    if __name__ == "__main__":
        input_1 = input("Type the first date: ")
        input_2 = input("Type the second date: ")
        print(f"The day difference between the two dates is: {main(input_1, input_2)}.")")
        """
    )

conversation.predict(input="what does the code do?")