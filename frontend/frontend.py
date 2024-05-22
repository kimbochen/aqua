import os
import sys
import requests
import gradio as gr


API_ENDPOINT = f"http://{os.environ['SERVER_IP']}:{os.environ['SERVER_PORT']}"
USER_ID = sys.argv[1].split('/')[2]
QTYPES = ['General', 'Assignment']
ASMT_MENU = [
    'Assignment 4 Question 1',
    'Assignment 4 Question 3',
    'Assignment 4 Question 4',
    'Assignment 4 Question 5',
    'Assignment 4 Programming',
    'Assignment 5 Question 4',
    'Assignment 5 Programming'
]


def main():
    theme = gr.themes.Default(spacing_size='lg', text_size='lg')

    with gr.Blocks(theme=theme) as aqua_ui:
        # UI blocks
        gr.Markdown(f'# Hello, {USER_ID}')

        with gr.Group():
            with gr.Row():
                qtype_menu = gr.Dropdown(QTYPES, show_label=False)
                asmt_menu = gr.Dropdown(ASMT_MENU, visible=False, show_label=False)
            with gr.Row():
                qbox = gr.Textbox(placeholder='Select a question type above', interactive=False, show_label=False, scale=9)
                submit_btn = gr.Button('Submit', size='sm', interactive=False, scale=1)

        with gr.Group():
            abox = gr.Textbox(label='Answer', interactive=False, autoscroll=False)
            with gr.Row():
                good_btn = gr.Button('👍', size='sm')
                bad_btn = gr.Button('👎', size='sm')

        sbox = gr.Textbox(label='Sources', interactive=False, autoscroll=False)

        clear_btn = gr.ClearButton(components=[qbox, abox, sbox], size='sm')

        # UI logic
        qa_id = gr.State([])
        qtype_menu.input(
            show_asmt_menu_fn, inputs=[qtype_menu],
            outputs=[asmt_menu, qbox, submit_btn, clear_btn]
        )
        asmt_menu.input(lambda: toggle_qa_ui(True, 'Enter your question'), outputs=[qbox, submit_btn, clear_btn])
        gr.on(
            triggers=[qbox.submit, submit_btn.click], fn=submit_query,
            inputs=[qbox, qtype_menu, asmt_menu], outputs=[abox, sbox, qa_id]
        )
        qbox.change(lambda query: [gr.update(interactive=(query != ''))] * 2, inputs=[qbox], outputs=[good_btn, bad_btn])
        good_btn.click(lambda rid: submit_feedback(rid, 1), inputs=[qa_id], outputs=[good_btn, bad_btn])
        bad_btn.click(lambda rid: submit_feedback(rid, -1), inputs=[qa_id], outputs=[good_btn, bad_btn])


    aqua_ui.launch(
        server_name='0.0.0.0',
        root_path=f'{sys.argv[1]}/aqua',
        server_port=int(sys.argv[2])
    )


def show_asmt_menu_fn(qtype):
    show_asmt_menu = (qtype == 'Assignment')
    prompt = 'Select an assignment question' if show_asmt_menu else 'Enter your question'
    asmt_menu_state = [gr.update(visible=show_asmt_menu, interactive=True)]
    qa_ui_state = toggle_qa_ui(not show_asmt_menu, prompt)
    return asmt_menu_state + qa_ui_state


def toggle_qa_ui(toggle, prompt):

    return [
        gr.update(value=None, placeholder=prompt, interactive=toggle),  # qbox
        gr.update(interactive=toggle),                                  # submit_btn
        gr.update(interactive=toggle)                                   # clear_btn
    ]


def submit_query(query, qtype, asmtq):
    if qtype == 'Assignment':
        qtype = asmtq.replace('Assignment ', 'asmt').replace(' Question ', '-q').replace(' Programming', '-prog')
    else:
        qtype = qtype.replace('Reading ', '').lower()

    resp = requests.get(f'{API_ENDPOINT}/query', params={'query': query, 'user_id': USER_ID, 'qtype': qtype})
    print(f'Making request {resp.url}')
    resp = resp.json()

    return (
        gr.update(value=resp['answer']),   # abox
        gr.update(value=resp['sources']),  # sbox
        resp['qa_id']                      # qa_id
    )


def submit_feedback(qa_id, verdict):
    resp = requests.post(f'{API_ENDPOINT}/feedback', params={'qa_id': qa_id, 'user_id': USER_ID, 'verdict': verdict})
    print(f'Making post request: {resp.url}')
    return [gr.update(interactive=False)] * 2  # good_btn, bad_btn


if __name__ == '__main__':
    main()
