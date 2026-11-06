import Foundation
import Vision
import PDFKit
import AppKit

// Native offline OCR. Input: JSON [{input: absolute PDF/image, output: text path}].
let jobs = try JSONSerialization.jsonObject(with: Data(contentsOf: URL(fileURLWithPath: CommandLine.arguments[1]))) as! [[String:String]]
for job in jobs {
    let input=job["input"]!, output=job["output"]!
    if FileManager.default.fileExists(atPath: output) { continue }
    var texts:[String]=[]
    func recognize(_ image:CGImage, _ page:Int) throws {
        let req=VNRecognizeTextRequest()
        req.recognitionLevel = .accurate
        req.recognitionLanguages = ["en-US"]
        req.usesLanguageCorrection = false
        try VNImageRequestHandler(cgImage:image).perform([req])
        let observations=(req.results ?? []).sorted {
            if abs($0.boundingBox.midY - $1.boundingBox.midY) < 0.008 { return $0.boundingBox.minX < $1.boundingBox.minX }
            return $0.boundingBox.midY > $1.boundingBox.midY
        }
        texts.append("\n--- PAGE \(page) ---\n" + observations.compactMap{$0.topCandidates(1).first?.string}.joined(separator:"\n"))
    }
    do {
        if input.lowercased().hasSuffix(".pdf") {
            guard let pdf=PDFDocument(url:URL(fileURLWithPath:input)) else {continue}
            for i in 0..<pdf.pageCount {
                try autoreleasepool {
                    guard let page=pdf.page(at:i) else {return}
                    let bounds=page.bounds(for:.mediaBox), scale:CGFloat=2.5
                    guard let ctx=CGContext(data:nil,width:Int(bounds.width*scale),height:Int(bounds.height*scale),bitsPerComponent:8,bytesPerRow:0,space:CGColorSpaceCreateDeviceRGB(),bitmapInfo:CGImageAlphaInfo.premultipliedLast.rawValue) else {return}
                    ctx.setFillColor(NSColor.white.cgColor);ctx.fill(CGRect(x:0,y:0,width:bounds.width*scale,height:bounds.height*scale))
                    ctx.scaleBy(x:scale,y:scale);page.draw(with:.mediaBox,to:ctx)
                    if let img=ctx.makeImage(){try recognize(img,i+1)}
                }
            }
        } else if let image=NSImage(contentsOfFile:input), let cg=image.cgImage(forProposedRect:nil,context:nil,hints:nil) {try recognize(cg,1)}
        try texts.joined(separator:"\n").write(toFile:output,atomically:true,encoding:.utf8)
        print("OCR \(URL(fileURLWithPath:input).lastPathComponent) \(texts.count) pages",terminator:"\n");fflush(stdout)
    } catch { print("ERROR \(input): \(error)") }
}
