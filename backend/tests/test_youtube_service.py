from backend.services.youtube_service import process_youtube_url

url = input("Enter YouTube URL: ")

try:
    result = process_youtube_url(url)

    print("\n=== SUCCESS ===")
    print(result)

except Exception as e:
    print("\n=== ERROR ===")
    print(type(e).__name__)
    print(e)