import gradio as gr
from isnet_pro.video2frame import video2frame,ui_frame2video
from isnet_pro.Inference2 import pic_generation_single,pic_generation2,ui_invert_image, mask_generate
import modules.shared as shared

from utils import  merge_overlapping_grids_linear, divide_and_save_Overlap
import modules.generation_parameters_copypaste as parameters_copypaste
from BFS import bfs_full
from Pixelinate import pixelinate

from modules import script_callbacks

function_dict = {
    "pixelinate": pixelinate,
    "bfs": bfs_full,
}

def gr_show(visible=True):
    return {"visible": visible, "__type__": "update"}

def on_ui_tabs():
    # pixelate post-processing
    with gr.Blocks(analytics_enabled=False) as postprocessing_interface:
        # split image into several patches
        with gr.Tab(label="Image Split"):
            with gr.Blocks(analytics_enabled=False):
                with gr.Row():
                    raw_image = gr.Image(label="raw image", elem_id="raw_image", type="filepath")
                with gr.Row():
                    patch_height = gr.Number(value=128, label="patch height", precision=1, interactive=True, placeholder="height of patches")
                    patch_width = gr.Number(value=128, label="patch width", precision=1, interactive=True, placeholder="width of patches")
                    patch_overlaph = gr.Number(value=32, label="overlaph", precision=1, interactive=True, placeholder="overlap height of patches")
                    patch_overlapw = gr.Number(value=32, label="overlapw", precision=1, interactive=True, placeholder="overlap width of patches")
                with gr.Row():
                    patches_output_dir = gr.Textbox(label="网格图输出地址\\patch_output_dir", placeholder="output\\folder")
                with gr.Column():
                    split_button = gr.Button(value="Split Image")
                    output_massage = gr.Textbox(label="")
                    split_button.click(
                        divide_and_save_Overlap,
                        [raw_image,
                         patch_height, patch_width,
                         patch_overlaph, patch_overlapw,
                         patches_output_dir],
                        [output_massage])

        # Merge img2img output patches into an whole image
        with gr.Tab(label="Patches Merge"):
            with gr.Blocks(analytics_enabled=False):
                with gr.Row():
                    with gr.Tabs():
                        with gr.TabItem(label='Merge Input'):
                            with gr.Column():
                                with gr.Column():
                                    with gr.Row():
                                        patch_input_dir = gr.Textbox(label='网格图输入地址\\patch_input_dir', placeholder='input\\folder')
                                        image_output_dir = gr.Textbox(label='图片输出地址\\image_output_dir', placeholder='output\\folder')
                                    with gr.Row():
                                        image_height = gr.Number(value=-1, label="image height", precision=1, interactive=True, placeholder="height for merged images")
                                        image_width = gr.Number(value=-1, label="image width", precision=1, interactive=True, placeholder="width for merged images")
                                    with gr.Row():
                                        patch_height = gr.Number(value=128, label="patch height", precision=1, interactive=True, placeholder="height of patches")
                                        patch_width = gr.Number(value=128, label="patch width", precision=1, interactive=True, placeholder="width of patches")
                                        patch_overlaph = gr.Number(value=32, label="overlaph", precision=1, interactive=True, placeholder="overlap height of patches")
                                        patch_overlapw = gr.Number(value=32, label="overlapw", precision=1, interactive=True, placeholder="overlap width of patches")
                    with gr.Tabs():
                        with gr.TabItem(label="Merge Output"):
                            with gr.Row():
                                result_image = gr.outputs.Image(type="pil")
                            with gr.Row():
                                merge_button = gr.Button(value="Merge Image") 
                                merge_button.click(merge_overlapping_grids_linear, 
                                                   [patch_input_dir, image_height, 
                                                    image_width, patch_height, 
                                                    patch_width, patch_overlaph, 
                                                    patch_overlapw], 
                                                    result_image)   

        # unify the RGB value of various color blocks
        with gr.Tab(label="Unify-RGB"):
            def handle_dropdown_change(choice, slider_visible):
                if str(choice) == "bfs":
                    return True
                else:
                    return False
            
            def unify_button_click(dropdown_choice, image_path, slider_value):
                if dropdown_choice in function_dict.keys():
                    fn = function_dict[dropdown_choice]
                result_image = fn(image_path, slider_value)
                return result_image
            


            with gr.Blocks(analytics_enabled=False):
                slider_visible = gr.State(False)  # 初始化状态为False，即滑块初始不可见
                with gr.Row():
                    with gr.Tabs():
                        with gr.TabItem(label="Unified Image"):
                            with gr.Row():
                                output_iamge = gr.outputs.Image(type="pil")

                    with gr.Tabs():
                        with gr.TabItem(label="Input image"):
                            with gr.Row():
                                # input image
                                input_image = gr.Image(label="input image", elem_id="input_image", type="filepath")
                
                            with gr.Column():      
                                build_method = gr.Dropdown(
                                    value=list(function_dict.keys())[0], 
                                    choices=[name for name in function_dict.keys()],
                                    placeholder="unify method to be used",
                                    label="unify method to be used",
                                    elem_id="Unify-RGB_build_method",
                                )
                                slider = gr.Slider(minimum=0, maximum=100, label="color distance", visible=slider_visible)
                                
                            with gr.Row():
                                unify_button = gr.Button(value="Unify RGB")
                                unify_button.click(
                                    fn=unify_button_click,
                                    inputs=[build_method, input_image, slider],
                                    outputs=output_iamge
                                    )
                            
                # unify methods
                build_method.change(fn=handle_dropdown_change, 
                                    inputs=build_method, 
                                    outputs=slider_visible)
                #with gr.Row():
                    # show unified image
    return [(postprocessing_interface, "Pixelinate", "pixelinate")]

script_callbacks.on_ui_tabs(on_ui_tabs)