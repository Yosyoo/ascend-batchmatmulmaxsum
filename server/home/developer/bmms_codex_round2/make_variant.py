from pathlib import Path
root=Path(__file__).resolve().parent
s=(root/'reference/kernel.asc').read_text()
s=s.replace('const int32_t core = GetBlockIdx();','const int32_t core = GetBlockIdx();\n    const int32_t rows = ns == 1 ? mt * 8 : m;\n    const int32_t chunk = rows < 1024 ? (rows + 7) / 8 * 8 : 1024;')
s=s.replace('TQue<TPosition::VECIN, 1> input, sumInput;', 'TQue<TPosition::VECIN, 2> input;\n        TQue<TPosition::VECIN, 1> sumInput;')
s=s.replace('temp, reduced, rowMax;', 'temp, reduced, rowMax, total;')
s=s.replace('pipe.InitBuffer(input, 1,', 'pipe.InitBuffer(input, 2,')
s=s.replace('(m + 7) / 8 * 32', 'chunk * 4')
s=s.replace('pipe.InitBuffer(rowMax, chunk * 4);','pipe.InitBuffer(rowMax, chunk * 4);\n        pipe.InitBuffer(total, 32);')
old='''                output.EnQue(running); running = output.DeQue<float>();
                DataCopyExtParams cp{1, (uint32_t)cm * 4, 0, 0, 0};
                DataCopyPad(mg[((int64_t)batch * ns + part) * m + mi], running, cp);'''
new='''                if (ns == 1) {
                    // Each M tile writes one sum, padded to a full DMA block.
                    ReduceSum(rbuf, running, temp.Get<float>(), cm);
                    Duplicate(running, 0.0f, 8);
                    Adds(running, rbuf, 0.0f, 1);
                    output.EnQue(running); running = output.DeQue<float>();
                    DataCopyExtParams cp{1, 32, 0, 0, 0};
                    DataCopyPad(mg[(int64_t)batch * rows + (mi / tileM) * 8], running, cp);
                } else {
                    output.EnQue(running); running = output.DeQue<float>();
                    DataCopyExtParams cp{1, (uint32_t)cm * 4, 0, 0, 0};
                    DataCopyPad(mg[((int64_t)batch * ns + part) * m + mi], running, cp);
                }'''
assert old in s;s=s.replace(old,new)
start=s.index('        auto sumTemp = temp.Get<float>();')
end=s.index('\n    }\n}\n\ntemplate<class T>',start)
s=s[:start]+'''        auto sumTemp = temp.Get<float>();
        for (int32_t batch = core; batch < batches; batch += GetBlockNum()) {
            auto accum = total.Get<float>();
            Duplicate(accum, 0.0f, 8);
            for (int32_t off = 0; off < rows; off += chunk) {
                int32_t count = rows - off < chunk ? rows - off : chunk;
                auto acc = rowMax.Get<float>();
                if (ns > 1) Duplicate(acc, -3.402823466e+38f, count);
                for (int32_t part = 0; part < ns; ++part) {
                    auto x = sumInput.AllocTensor<float>();
                    DataCopyExtParams cp{1, (uint32_t)count * 4, 0, 0, 0};
                    DataCopyPadExtParams<float> pad{false, 0, 0, 0};
                    DataCopyPad(x, mg[((int64_t)batch * ns + part) * rows + off], cp, pad);
                    sumInput.EnQue(x); x = sumInput.DeQue<float>();
                    if (ns == 1) ReduceSum(rbuf, x, sumTemp, count);
                    else Max(acc, acc, x, count);
                    sumInput.FreeTensor(x);
                }
                if (ns > 1) ReduceSum(rbuf, acc, sumTemp, count);
                Add(accum, accum, rbuf, 1);
            }
            auto out = output.AllocTensor<float>();
            Adds(out, accum, 0.0f, 8);
            output.EnQue(out); out = output.DeQue<float>();
            DataCopyExtParams op{1, 4, 0, 0, 0};
            DataCopyPad(yg[batch], out, op);
            output.FreeTensor(out);
        }''' +s[end:]
# Enough workspace for the compact padded partial sums even when M < 8.
s=s.replace('((size_t)b * ns * m * 4 + 511)', '((size_t)b * ns * std::max(m, ((m + tileM - 1) / tileM) * 8) * 4 + 511)')
(root/'pipeline/kernel.asc').write_text(s)
p=root/'bench.asc'; s=p.read_text().replace('int32_t deviceId = 0;', 'int32_t deviceId = 1;');p.write_text(s)
