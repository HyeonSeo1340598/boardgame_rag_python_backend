# 필요 라이브러리
# pip install -r requirements.txt

# import os
# from langchain_upstage import UpstageDocumentParseLoader, UpstageEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_chroma import Chroma
# from langchain.docstore.document import Document

# # API 키 설정
# os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
# os.environ["UPSTAGE_API_KEY"] = "up_p4zbJL1uBqSwlEs3739EZ9AQpeWWOh"

# # 처리할 PDF 목록 (이름과 파일 경로)
# pdf_list = [
#     {"game": "카탄", "file": "pdfs/katan.pdf"},
#     {"game": "스플렌더", "file": "pdfs/splendor.pdf"},
#     # 더 추가하고 싶으면 여기에 game/file 계속 추가만 하면 됨!
# ]

# # 공통 설정
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
# embedding = UpstageEmbeddings(model="solar-embedding-1-large")
# persist_dir = "chroma_db"  # 영구 저장될 디렉토리

# # Chroma DB 초기화 (기존 DB 유지 + 추가 저장용)
# vectorstore = Chroma(
#     persist_directory=persist_dir,
#     embedding_function=embedding
# )

# # 반복 처리
# for entry in pdf_list:
#     game_name = entry["game"]
#     file_path = entry["file"]

#     print(f"\n📥 처리 중: {game_name} ({file_path})")

#     try:
#         # 1. 문서 파싱
#         loader = UpstageDocumentParseLoader(
#             file_path=file_path,
#             output_format='html',
#             coordinates=False
#         )
#         parsed_docs = loader.load()

#         # 2. 메타데이터 추가
#         docs = [
#             Document(
#                 page_content=doc.page_content,
#                 metadata={"game": game_name}
#             )
#             for doc in parsed_docs
#         ]

#         # 3. 문서 분할
#         chunks = text_splitter.split_documents(docs)

#         # 4. 임베딩 + 벡터DB 저장
#         vectorstore.add_documents(chunks)

#         print(f"저장 완료: {game_name} ({len(chunks)} chunks)")

#     except Exception as e:
#         print(f"오류 발생: {game_name} 처리 실패 - {str(e)}")

# # 마지막에 DB 저장 완료
# # vectorstore._client.persist() # 저장하는 코드가 필요 없어짐....
# print("\n📦 모든 게임 룰이 벡터 DB에 저장되었습니다!")






# ------------------------------------------- 아래는 Pinecone version 입니다 -------------------------------------------

import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_upstage import UpstageDocumentParseLoader, UpstageEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain.docstore.document import Document

# .env 파일에서 환경변수 로드
load_dotenv()

# 환경변수 가져오기
openai_key = os.getenv("OPENAI_API_KEY")
upstage_key = os.getenv("UPSTAGE_API_KEY")
pinecone_key = os.getenv("PINECONE_API_KEY")

# 환경 변수 설정 (또는 .env로 관리 가능)
os.environ["OPENAI_API_KEY"] = openai_key
os.environ["UPSTAGE_API_KEY"] = upstage_key
os.environ["PINECONE_API_KEY"] = pinecone_key

# Pinecone 클라이언트 생성 (init 대신)
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])

# 인덱스 이름
index_name = "boardgame-rag"

# PDF 목록 정의
pdf_list = [
    {"game": "테스트", "file": "pdfs/test.pdf", "namespace": "test"},
]

# 공통 설정
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
embedding = UpstageEmbeddings(model="solar-embedding-1-large")

# PDF 처리 루프
for entry in pdf_list:
    game_name = entry["game"]
    file_path = entry["file"]
    namespace = entry["namespace"]

    print(f"\n📥 처리 중: {game_name} ({file_path})")

    try:
        # 1. 문서 파싱
        loader = UpstageDocumentParseLoader(
            file_path=file_path,
            output_format='html',
            coordinates=False
        )
        parsed_docs = loader.load()

        for doc in parsed_docs:
            print(doc.page_content[:500])  # 앞부분 일부 출력

        # 2. 메타데이터 추가
        docs = [
            Document(
                page_content=doc.page_content,
                metadata={"game": game_name}
            )
            for doc in parsed_docs
        ]

        # 3. 문서 분할
        chunks = text_splitter.split_documents(docs)

        # 4. Pinecone에 벡터 저장
        vectorstore = PineconeVectorStore.from_documents(
            documents=chunks,
            embedding=embedding,
            index_name=index_name,
            namespace=namespace
        )

        print(f"✅ 저장 완료: {game_name} ({len(chunks)} chunks)")

    except Exception as e:
        print(f"❌ 오류 발생: {game_name} 처리 실패 - {str(e)}")

print("\n📦 모든 게임 룰이 Pinecone에 저장되었습니다!")