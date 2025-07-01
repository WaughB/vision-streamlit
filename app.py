# filename: app.py

import streamlit as st
import ollama

st.set_page_config(page_title="Llama 3.2‑Vision Demo", layout="centered")

st.title("🖼️ Llama 3.2‑Vision with Streamlit")
st.write("Upload an image and ask a question about it.")

# Image upload
uploaded = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])
question = st.text_input("Ask a question:")

if st.button("Analyze") and uploaded and question:
    # Save the uploaded image
    img_bytes = uploaded.read()
    with open("temp_image.png", "wb") as f:
        f.write(img_bytes)

    st.image(img_bytes, caption="Uploaded image", use_column_width=True)

    # Call the Ollama model
    try:
        with st.spinner("Thinking..."):
            response = ollama.chat(
                model="llama3.2-vision",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a maritime vessel analysis assistant. Given an image of a ship, "
                            "your job is to extract and respond clearly with the following:\n\n"
                            "- Name of the vessel (if visible)\n"
                            "- IMO number (International Maritime Organization number, usually 7 digits)\n"
                            "- IMSI (International Mobile Subscriber Identity, if relevant/visible)\n"
                            "- Name of the company that owns or operates the vessel (based on visible markings)\n\n"
                            "If any of the above are not clearly visible or determinable, say 'Not visible' for that field."
                        ),
                    },
                    {"role": "user", "content": question, "images": ["temp_image.png"]},
                ],
            )
        # Display the response
        answer = getattr(response, "message", {}).get("content", "No content returned.")
        if not answer:
            answer = "No content returned from the model."
        st.subheader("Answer")
        st.write(answer)
    except Exception as e:
        st.error(f"Failed to get response: {e}")
