from .misc import setup, executor


if __name__ == "__main__":
    setup()
    print("starting polling")
    executor.start_polling(reset_webhook=True)
