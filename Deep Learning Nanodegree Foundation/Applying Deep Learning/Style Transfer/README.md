# Style Transfer

Style transfer allows you to take famous paintings, and recreate your own images in their styles! The network learns the underlying techniques of those paintings and figures out how to apply them on its own. This model was trained on the styles of famous paintings and is able to transfer those styles to other images and even [videos!](https://www.youtube.com/watch?v=xVJwwWQlQ1o)

The network has been trained on a few different styles ([here](https://github.com/lengstrom/fast-style-transfer/tree/master/examples/style)) and saved into [checkpoint files](https://drive.google.com/drive/folders/0B9jhaT37ydSyRk9UX0wwX3BpMzQ). Checkpoint files contain all the information about the trained network to apply styles to new images.

I used it to style our family dog Daphne in various styles


To try it out yourself, you can find the code in the [fast-style-transfer](https://github.com/lengstrom/fast-style-transfer) repo.

### Transferring styles

- Download the Zip archive from the fast-style-transfer repository and extract it. .
- Download the Rain Princess checkpoint from [here](https://d17h27t6h515a5.cloudfront.net/topher/2017/January/587d1865_rain-princess/rain-princess.ckpt). Put it in the fast-style-transfer folder. A checkpoint file is a model that already has tuned parameters. By using this checkpoint file, we won't need to train the model and can get straight to applying it.
- Copy the image you want to style into the fast-style-transfer folder.
- In your terminal, navigate to the fast-style-transfer folder and enter `python evaluate.py --checkpoint ./rain-princess.ckpt --in-path <path_to_input_file> --out-path ./output_image.jpg`

Note: Be careful with the size of the input image. The style transfer can take quite a while to run on larger images.