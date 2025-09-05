import cv2
import typing
import numpy as np

from mltu.inferenceModel import OnnxInferenceModel
from mltu.utils.text_utils import ctc_decoder, get_cer

class ImageToWordModel(OnnxInferenceModel):
    def __init__(self, char_list: typing.Union[str, list], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.char_list = char_list

    def predict(self, image: np.ndarray):
        # Derive input spatial size from ONNX session if input_shapes is not available
        try:
            # self.model is expected to be an onnxruntime.InferenceSession
            onnx_inputs = self.model.get_inputs()
            if not onnx_inputs:
                raise RuntimeError("ONNX model has no inputs")
            ishape = onnx_inputs[0].shape  # [N, H, W, C] typically
            # Handle dynamic dims (None)
            h = int(ishape[1]) if isinstance(ishape[1], (int,)) else None
            w = int(ishape[2]) if isinstance(ishape[2], (int,)) else None
            if h is None or w is None:
                # Fallback to original image size if dynamic
                target_size = (image.shape[1], image.shape[0])
            else:
                target_size = (w, h)  # cv2.resize expects (W, H)
        except Exception:
            # Ultimate fallback: do not resize
            target_size = (image.shape[1], image.shape[0])

        image = cv2.resize(image, target_size)

        # Do NOT normalize here; the exported ONNX graph already divides by 255
        image_pred = np.expand_dims(image, axis=0).astype(np.float32)

        # Resolve input/output names if base class didn't set them
        try:
            input_name = self.input_names[0]  # type: ignore[attr-defined]
        except Exception:
            input_name = self.model.get_inputs()[0].name
        try:
            output_names = self.output_names  # type: ignore[attr-defined]
        except Exception:
            output_names = [self.model.get_outputs()[0].name]

        preds = self.model.run(output_names, {input_name: image_pred})[0]

        text = ctc_decoder(preds, self.char_list)[0]

        return text

if __name__ == "__main__":
    import pandas as pd
    from tqdm import tqdm
    from mltu.configs import BaseModelConfigs

    configs = BaseModelConfigs.load("Results/202212211205/configs.yaml")

    model = ImageToWordModel(model_path=configs.model_path, char_list=configs.vocab)

    df = pd.read_csv("Results/202212211205/val.csv").values.tolist()

    accum_cer = []
    for image_path, label in tqdm(df):
        image = cv2.imread(image_path.replace("\\", "/"))

        prediction_text = model.predict(image)

        cer = get_cer(prediction_text, label)
        print(f"Image: {image_path}, Label: {label}, Prediction: {prediction_text}, CER: {cer}")

        accum_cer.append(cer)

    print(f"Average CER: {np.average(accum_cer)}")