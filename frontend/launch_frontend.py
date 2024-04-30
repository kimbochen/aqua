import os
import sys
from pathlib import Path

import gradio as gr
import requests

API_ENDPOINT = f"http://{os.environ['SERVER_IP']}:{os.environ['SERVER_PORT']}"
USER_ID = sys.argv[1].split('/')[2]
QA_ID = None

ASMTQ_IDS = [
    (1, 5), (1, 7), (1, 8), (1, 9), (1, 10),
    (2, 1), (2, 11), (2, 14),
    (3, 1), (3, 2), (3, 3), (3, 7), (3, 9), (3, 10), (3, 11), (3, 12), (3, 15), (3, 16)
]
MENU_TO_FNAME = {
    f'Assignment {asmt_id} Question {q_id}': f'asmt{asmt_id}-q{q_id}'
    for asmt_id, q_id in ASMTQ_IDS
}
MENU_TO_FNAME['Assignment 2 Programming'] = 'asmt2-qprog'
MENU_TO_FNAME['Assignment 3 Programming'] = 'asmt3-qprog'


def query_aqua(qtype_val, query, asmtq_menu_val):
    global QA_ID, USER_ID

    if qtype_val == 'General':
        response = requests.get(API_ENDPOINT, params={'query': query, 'user_id': USER_ID}).json()
    elif qtype_val == 'Assignment':
        query_params = {'query': query, 'user_id': USER_ID, 'asmtq_fname': MENU_TO_FNAME[asmtq_menu_val]}
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
    return gr.update(visible=show_textbox, interactive=show_textbox)


def main():
    theme = gr.themes.Default(spacing_size='lg', text_size='lg')

    with gr.Blocks(theme=theme) as aqua:
        with gr.Row():
            qtype = gr.Dropdown(['General', 'Assignment'], value='General', label='Question Type')
            asmtq_menu = gr.Dropdown(list(MENU_TO_FNAME.keys()), label='Select a question.', visible=False)

        qbox = gr.Textbox(label='Enter your question')
        abox = gr.Textbox(label='Answer', interactive=False, autoscroll=False)

        with gr.Row():
            submit_btn = gr.Button('Submit', size='sm')
            clear_btn = gr.ClearButton(components=[qbox, abox], size='sm')
            flag_btn = gr.Button('Good Response', size='sm', interactive=False)

        # Question type logic
        qtype.input(select_index, inputs=[qtype], outputs=[asmtq_menu])

        # Question submission logic
        gr.on(
            triggers=[qbox.submit, submit_btn.click], fn=query_aqua,
            inputs=[qtype, qbox, asmtq_menu], outputs=abox
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
