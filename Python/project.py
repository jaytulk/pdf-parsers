from PyPDF2 import PdfFileReader, PdfFileWriter
from re import search
import time


def splitPdf(pdfFilePath, identifierMatchingStrategy):
    startingTime = time.perf_counter()
    pdfFileObject = open(pdfFilePath, 'rb')

    pdfReader = PdfFileReader(pdfFileObject)

    pageCount = pdfReader.numPages

    filePathParts = pdfFilePath.split('/')
    pdfFileName = filePathParts[len(filePathParts) - 1].split('.pdf')[0]

    currentPageIndex = 1

    for _ in range(pageCount - currentPageIndex):
        pageObject = pdfReader.getPage(currentPageIndex)
        identifier = getIdentifier(pageObject, identifierMatchingStrategy)

        pdfWriter = PdfFileWriter()
        pdfWriter.addPage(pageObject)

        with open(f"Python/output/{pdfFileName}-{identifier}.pdf", "wb") as file:
            pdfWriter.write(file)

        currentPageIndex = currentPageIndex + 1

    pdfFileObject.close()
    endingTime = time.perf_counter()
    print(
        f"Finished processing {pageCount - 1} pages from {pdfFileName}.pdf in {endingTime - startingTime:0.4f} seconds")


def getIdentifier(pageObject, identifierMatchingStrategy):
    text = pageObject.extractText()

    identifierStartingIndex = 0
    identifierEndingIndex = 0
    identifier = ''

    if(identifierMatchingStrategy == 'billDateStrategy'):
        billDateMatch = search('(\d{2}\/\d{2}\/\d{6}\/\d{2}\/\d{4})', text)
        billDate = billDateMatch[0]
        identifierStartingIndex = billDateMatch.start() + len(billDate)
        identifierEndingIndex = identifierStartingIndex + 14

        # The identifier could either have a leading newline or trailing $ character
        identifier = text[identifierStartingIndex:identifierEndingIndex].replace(
            '\n', '').replace('$', '')
    elif (identifierMatchingStrategy == 'chargeLineStrategy'):
        chargeLine = search('\$-?[\d|,]+.\d{2}(\d{13})', text)[1]
        identifierStartingIndex = text.index(chargeLine)
        identifierEndingIndex = identifierStartingIndex + 13

        # The identifier could have a trailing newline
        identifier = text[identifierStartingIndex:identifierEndingIndex].replace(
            '\n', '')
    else:
        raise Exception("Invalid file identifier matching strategy")

    return identifier


def main():
    print('Getting to work...')

    pathToPdf = 'Python/assets/356024_07_SCPWW_EB_USPS.pdf'
    splitPdf(pathToPdf, 'billDateStrategy')

    pathToPdf = 'Python/assets/356024_08_SCPWW_WB_USPS.pdf'
    splitPdf(pathToPdf, 'chargeLineStrategy')

    print('All Done!')


if __name__ == "__main__":
    main()
