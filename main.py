from models.unet_3d import Unet3D

model_info = {
    'input_shape': (256, 256, 3, 8),
    'name': 'loly',
    'description': "first test of the experimentation manager",
    'n_base_filters': 16,
    'classes': ('Potatoes', 'Wheat', 'Grapes'),
    'palette': ('ff00ff', 'ff00ff', 'ff00ff'),
    'dropout': 0.05,
    'depth': 4,
    'pool_shape': (2, 2, 1),
    'final_activation': 'sigmoid',
    'batchnorm': True

}

exp_info = {
    'train_size': 5000,
    'val_size': 250,
    'epochs': 10,
    'batch_size': 8,
    'loss_function': 'binairy_crossentropy',
    'training_time': 25645,
    'save_location': '/bla/bla/sfsdf/dfd/toto'
}

unet_3d = Unet3D(model_info)

model = unet_3d.get_model(db_file="test.db")


exp = model.add_experiment(exp_info)

#training code

res_info = {
    'status': 'Success',
    'train_loss': 0.06,
    'val_loss': 0.09,
    'train_accuracy': 98.99,
    'val_accuracy': 96.98
}

exp.add_result(result_info=res_info)


# print(model.summary())