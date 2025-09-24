
def main():
    print("Hello from ainvest!")
    app = agent_os.get_app()
    agent_os.serve(app="demo:app", port=7777)

if __name__ == "__main__":
    main()
