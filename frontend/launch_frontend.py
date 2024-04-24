import os
import sys

import gradio as gr
import requests

API_ENDPOINT = f"http://{os.environ['SERVER_IP']}:{os.environ['SERVER_PORT']}"
USER_ID = sys.argv[1].split('/')[2]
QA_ID = None


def query_aqua(qtype_val, query, asmt_id, q_id):
    global QA_ID, USER_ID

    if qtype_val == 'General':
        response = requests.get(API_ENDPOINT, params={'query': query, 'user_id': USER_ID}).json()
    elif qtype_val == 'Assignment':
        query_params = {'query': query, 'user_id': USER_ID, 'asmt_id': asmt_id, 'q_id': q_id}
        response = requests.get(f'{API_ENDPOINT}/asmtq', params=query_params).json()
    else:
        response = {'answer': f'Please select a question type.', 'qa_id': None}

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
            qtype = gr.Dropdown(['General', 'Assignment'], value='General', label='Question Type')
            asmt_id = gr.Textbox(label='Assignment No.', visible=False)
            q_id = gr.Textbox(label='Question No.', visible=False)

        qbox = gr.Textbox(label='Enter your question')
        abox = gr.Textbox(label='Answer', interactive=False, autoscroll=False)

        with gr.Row():
            submit_btn = gr.Button('Submit', size='sm')
            clear_btn = gr.ClearButton(components=[qbox, abox], size='sm')
            flag_btn = gr.Button('Good Response', size='sm', interactive=False)

        # Question type logic
        qtype.input(select_index, inputs=[qtype], outputs=[asmt_id, q_id])

        # Question submission logic
        gr.on(
            triggers=[qbox.submit, submit_btn.click], fn=query_aqua,
            inputs=[qtype, qbox, asmt_id, q_id], outputs=abox
        )

        # Flag button logic
        qbox.change(lambda q_str: gr.update(interactive=(q_str != '')), inputs=qbox, outputs=flag_btn)
        flag_btn.click(flag_response, inputs=[qbox, abox], outputs=flag_btn)

    aqua.launch(
        server_name='0.0.0.0',
        root_path=f'{sys.argv[1]}/aqua',
        server_port=int(sys.argv[2])
    )


if __name__ == '__main__':
    main()
