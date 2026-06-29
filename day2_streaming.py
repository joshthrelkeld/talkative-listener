import asyncio

async def stream_audio_chunks():
    chunks = [
        "I need to",
        " schedule an",
        " appointment",
        " for Tuesday",
    ]
    for chunk in chunks:
        await asyncio.sleep(0.5)
        yield chunk

async def transcribe(stream):
    full_transcript = ""
    async for chunk in stream:
        full_transcript += chunk
        print(f"Partial transcript: {full_transcript}")
    print(f"\nFinal transcript: {full_transcript}")

async def main():
    stream = stream_audio_chunks()
    await transcribe(stream)

asyncio.run(main())