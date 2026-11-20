
from src.tools.tools import tavily_search,extract_webpage_content


def main():
    result = extract_webpage_content.invoke("https://en.wikipedia.org/wiki/WION")
    print(result)
    # query = input("Enter your search query: ")

    # # Execute Tavily search tool
    # results = tavily_search.invoke({"query": query})

    # print("\n===== TAVILY SEARCH RESULTS =====\n")

    # for index, result in enumerate(results, start=1):
    #     print(f"\nResult {index}")
    #     print(f"Title: {result['title']}")
    #     print(f"URL: {result['url']}")
    #     print(f"Content: {result['content']}")
    #     print("-" * 80)


if __name__ == "__main__":
    main()
