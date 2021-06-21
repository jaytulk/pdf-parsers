from PyPDF2 import PdfFileReader, PdfFileWriter
import re
import time


def splitPdf(pdfFilePath, accountNumberMatchingStrategy):
    startingTime = time.perf_counter()
    pdfFileObject = open(pdfFilePath, 'rb')

    pdfReader = PdfFileReader(pdfFileObject)

    pageCount = pdfReader.numPages

    filePathParts = pdfFilePath.split('/')
    pdfFileName = filePathParts[len(filePathParts) - 1].split('.pdf')[0]

    currentPageIndex = 1
    for _ in range(pageCount - currentPageIndex):
        pdfWriter = PdfFileWriter()

        pageObject = pdfReader.getPage(currentPageIndex)
        accountNumber = readAccountNumber(
            pageObject, accountNumberMatchingStrategy)

        outputPdf = f"./output/{pdfFileName}-{accountNumber}.pdf"

        pdfWriter.addPage(pageObject)

        with open(outputPdf, "wb") as file:
            pdfWriter.write(file)

        currentPageIndex = currentPageIndex + 1

    pdfFileObject.close()
    endingTime = time.perf_counter()
    print(
        f"Finished processing {pageCount - 1} bills from {pdfFileName}.pdf in {endingTime - startingTime:0.4f} seconds")


def readAccountNumber(pageObject, accountNumberMatchingStrategy):
    text = pageObject.extractText()

    accountNumberStartingIndex = 0
    accountNumberEndingIndex = 0

    if(accountNumberMatchingStrategy == 'billDateStrategy'):
        billDateMatch = re.search('(\d{2}\/\d{2}\/\d{6}\/\d{2}\/\d{4})', text)
        billDate = billDateMatch[0]
        accountNumberStartingIndex = billDateMatch.start() + len(billDate)
        accountNumberEndingIndex = accountNumberStartingIndex + 14
    elif (accountNumberMatchingStrategy == 'chargeLineStrategy'):
        chargeLine = re.search('\$-?[\d|,]+.\d{2}(\d{13})', text)[1]
        accountNumberStartingIndex = text.index(chargeLine)
        accountNumberEndingIndex = accountNumberStartingIndex + 13
    else:
        raise Exception("Invalid account number matching strategy")

    # The account number can either have a leading newline or trailing $ character
    accountNumber = text[accountNumberStartingIndex:accountNumberEndingIndex].replace(
        '\n', '').replace('$', '')

    return accountNumber


def main():
    print('Getting to work...')

    pathToPdf = './assets/356024_07_SCPWW_EB_USPS.pdf'
    splitPdf(pathToPdf, 'billDateStrategy')

    pathToPdf = './assets/356024_08_SCPWW_WB_USPS.pdf'
    splitPdf(pathToPdf, 'chargeLineStrategy')

    print('All Done!')


if __name__ == "__main__":
    main()
