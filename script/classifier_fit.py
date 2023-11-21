import asyncio
import os

import dotenv
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve

from app.email_classifier_tfid import EmailClassifierTfid
from app.email_dao_mongo import EmailDaoMongo
from app.utils.secrets import get_secret


# Define an asynchronous main function
async def main():
    # Load environment variables from a .env file if it exists
    if dotenv.find_dotenv():
        dotenv.load_dotenv(dotenv.find_dotenv())

    # Initialize an instance of EmailDaoMongo for MongoDB connection
    email_dao = EmailDaoMongo("mongodb://127.0.0.1:27017", "tallulah", "emails_temp")

    # Read all emails from the database
    list_email = await email_dao.read_all()

    # Get the file path for the email classifier model from a secret
    path_file_model = get_secret("path_file_model")

    # Define a dictionary to adjust scores based on email categories
    dict_score_multiplier = {
        "General Breasties": 1.1,
        "General Info": 0.75,
        "In a trial": 1.1,
        "Interested in a trial": 1.2,
        "Newly Diagnosed": 1.6,
        "Partners": 2.1,
    }

    # Initialize an instance of EmailClassifierTfid with a specified number of features
    classfier = EmailClassifierTfid(40)

    # Fit the classifier with the email data, specifying the format and score multiplier dictionary
    classfier.fit(list_email, "csv", dict_score_multiplier)

    # Save the trained model to the specified file path
    classfier.save(path_file_model)

    # Extract the list of label options from the trained model
    list_label_option = classfier.model.list_label

    # Initialize lists to store true labels, predicted labels, and label scores
    list_label_true = []
    list_label_pred = []
    list_dict_label_score = []

    # Iterate through each email to evaluate the classifier's performance
    for email in list_email:
        # Check if the email content is non-empty
        if 0 < len(email.body["content"].strip()):
            # Get the true annotation label for the email
            annotation_true = email.get_annotation("csv")
            if annotation_true is not None:
                # Predict the annotation label using the classifier
                annotation_pred = classfier.predict_email_tags(email)[0]

                # Add the predicted annotation to the email in the database
                await email_dao.add_annotation(email.id, annotation_pred)

                # Append true and predicted labels, as well as label scores
                list_label_true.append(annotation_true.label)
                list_label_pred.append(annotation_pred.label)
                list_dict_label_score.append(annotation_pred.label_scores)

    # Generate and print confusion matrix
    matrix = confusion_matrix(list_label_true, list_label_pred, labels=list_label_option)
    print(matrix)

    # Print misclassifications between different labels in the confusion matrix
    for index, label in enumerate(list_label_option):
        for index2, label2 in enumerate(list_label_option):
            if matrix[index][index2] > 0:
                if label != label2:
                    print(f"{label} -> {label2}: {matrix[index][index2]}")

    # Print classification report with precision, recall, and F1-score
    print(classification_report(list_label_true, list_label_pred, labels=list_label_option, zero_division=0))

    # Calculate and print ROC AUC score for each label
    for label_option in list_label_option:
        list_y = []
        list_y_pred = []
        for index, label in enumerate(list_label_true):
            if label == label_option:
                list_y.append(1)
            else:
                list_y.append(0)
            list_y_pred.append(list_dict_label_score[index][label_option])
        print(f"{label_option.ljust(25)}:  {roc_auc_score(list_y, list_y_pred, average=None)}")


# Run the main function when the script is executed
if __name__ == "__main__":
    asyncio.run(main())
