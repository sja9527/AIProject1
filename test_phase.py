import torch
import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
import seaborn as sn
import pandas as pd

import general_methods


classes = ('NotAPerson', 'Person', 'PersonMask', ) # define 3 classes for training and testing datasets

def load_test_data():
    path = './test' # get testing set (labeled with subfolders) location
    testset = torchvision.datasets.ImageFolder(path,
                                                transform=transforms.Compose([
                                                    transforms.Resize((32, 32)),
                                                    transforms.CenterCrop(32),
                                                    transforms.ToTensor()])
                                                )
    test_loader = torch.utils.data.DataLoader(testset, batch_size=25, shuffle=True, drop_last=True)
    return test_loader

def confusion_matrix(preds, labels, conf_matrix):
    preds = torch.argmax(preds, 1)
    for p, t in zip(preds, labels):
        conf_matrix[p, t] += 1
    return conf_matrix

def test_phase():
    test_loader = load_test_data() # load test datasets
    net = torch.load('net.pkl') # load our net parameters from file

    correct = 0 # number of correct prediction
    total = 0 # number of total test cases
    batch_counter = 0

    # Below is for measure the precision, recall and F1-measure
    # for class "NotAPerson" 0
    tp_NotAPerson, fp_NotAPerson, fn_NotAPerson = 0, 0, 0

    # for class "Person" 1
    tp_Person, fp_Person, fn_Person = 0, 0, 0

    # for class "PersonMask" 2
    tp_PersonMask, fp_PersonMask, fn_PersonMask = 0, 0, 0

    # for confusion matrix
    conf_matrix = torch.zeros(3, 3)

    for images, labels in test_loader:
        outputs = net(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()
        batch_counter = batch_counter+1

        # print for test reason
        # print('\n*************For batch '+ str(batch_counter) + ' (25 images):*************')
        # print('%-15s %-70s' %  ("GroundTruth:", labels))  # print in format tensor([0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 2, 2, 1, 2, 0, 2, 0, 2, 2, 0, 2, 1, 1, 1, 1])
        # print('%-15s %s' % ("Predicted:", predicted)) # print in format tensor([0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 2, 2, 1, 2, 0, 2, 0, 2, 2, 0, 2, 1, 1, 1, 1])
        #
        # print('%-15s %s' % ('GroundTruth:', " ".join('%-12s' % classes[labels[number]] for number in range(labels.size(0)))))
        # print('%-15s %s' % ('Predicted:', " ".join('%-12s' % classes[predicted[number]] for number in range(labels.size(0)))))

        # for confusion matrix
        conf_matrix = confusion_matrix(outputs, labels, conf_matrix)

        for number in range(labels.size(0)):
            if classes[labels[number]] == "NotAPerson" and classes[predicted[number]] == "NotAPerson" :
                tp_NotAPerson = tp_NotAPerson +1
            elif classes[labels[number]] != "NotAPerson" and classes[predicted[number]] == "NotAPerson" :
                fp_NotAPerson = fp_NotAPerson +1
            elif classes[labels[number]] == "NotAPerson" and classes[predicted[number]] != "NotAPerson":
                fn_NotAPerson = fn_NotAPerson +1

            if classes[labels[number]] == "Person" and classes[predicted[number]] == "Person" :
                tp_Person = tp_Person +1
            elif classes[labels[number]] != "Person" and classes[predicted[number]] == "Person" :
                fp_Person = fp_Person +1
            elif classes[labels[number]] == "Person" and classes[predicted[number]] != "Person":
                fn_Person = fn_Person +1

            if classes[labels[number]] == "PersonMask" and classes[predicted[number]] == "PersonMask" :
                tp_PersonMask = tp_PersonMask +1
            elif classes[labels[number]] != "PersonMask" and classes[predicted[number]] == "PersonMask" :
                fp_PersonMask = fp_PersonMask +1
            elif classes[labels[number]] == "PersonMask" and classes[predicted[number]] != "PersonMask":
                fn_PersonMask = fn_PersonMask +1


    print('\nAccuracy of the test dataset : %.2f %%' % ((correct / total) * 100))
    # for printing precision, recall, f1measure
    general_methods.printTable([[tp_NotAPerson, fp_NotAPerson, fn_NotAPerson],
                               [tp_Person, fp_Person, fn_Person],
                               [tp_PersonMask,fp_PersonMask, fn_PersonMask]])

    # for confusion matrix
    print("\nconfusion matrix:")
    print(conf_matrix)

    df_cm = pd.DataFrame(conf_matrix.numpy(),
                         index=['NotAPerson', 'Person', 'PersonMask'],
                         columns=['NotAPerson', 'Person', 'PersonMask'])
    plt.figure(figsize=(10, 7))
    sn.heatmap(df_cm, annot=True, cmap="BuPu")
    plt.show()
