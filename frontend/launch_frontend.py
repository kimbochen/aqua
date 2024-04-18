import os
import sys

import gradio as gr
import requests

API_ENDPOINT = f"http://{os.environ['SERVER_IP']}:{os.environ['SERVER_PORT']}"
USER_ID = sys.argv[1]
QA_ID = None


def query_aqua(query):
    global QA_ID, USER_ID
    response = requests.get(API_ENDPOINT, params={'query': query, 'user_id': USER_ID}).json()
    QA_ID = response['qa_id']
    return response['answer']


def flag_response(q_str, a_str):
    requests.post(f'{API_ENDPOINT}/feedback', params={'qa_id': QA_ID, 'user_id': USER_ID})
    return gr.update(interactive=False)


def select_index(qtype_val):
    show_textbox = (qtype_val == 'Assignment')
    return (
        gr.update(visible=show_textbox, interactive=show_textbox),
        gr.update(visible=show_textbox, interactive=show_textbox)
    )


def main():
    theme = gr.themes.Default(spacing_size='lg', text_size='lg')

    with gr.Blocks(theme=theme) as aqua:
        with gr.Row():
            qtype = gr.Dropdown(['General', 'Assignment'], label='Question Type')
            asmt_id = gr.Textbox(label='Assignment No.', visible=False)
            q_id = gr.Textbox(label='Question No.', visible=False)

        qbox = gr.Textbox(label='Enter your question')
        abox = gr.Textbox(label='Answer', interactive=False, autoscroll=False, max_lines=12)

        with gr.Row():
            submit_btn = gr.Button('Submit', size='sm')
            clear_btn = gr.ClearButton(components=[qbox, abox], size='sm')
            flag_btn = gr.Button('Good Response', size='sm', interactive=False)

        # Question type logic
        qtype.input(select_index, inputs=[qtype], outputs=[asmt_id, q_id])

        # Question submission logic
        gr.on(
            triggers=[qbox.submit, submit_btn.click], fn=query_aqua,
            inputs=qbox, outputs=abox
        )

        # Flag button logic
        qbox.change(lambda q_str: gr.update(interactive=(q_str != '')), inputs=qbox, outputs=flag_btn)
        flag_btn.click(flag_response, inputs=[qbox, abox], outputs=flag_btn)

    aqua.launch(
        server_name='0.0.0.0',
        root_path=f'{USER_ID}/aqua',
        server_port=int(sys.argv[2])
    )


if __name__ == '__main__':
    main()
