#pragma once

#include <gunrock/algorithms/algorithms.hxx>
#include <vector>

namespace gunrock
{
namespace bfs
{

template <typename vertex_t> struct param_t
{
    std::vector<vertex_t> sources;

    param_t(const std::vector<vertex_t> &_sources) : sources(_sources)
    {
    }
};

template <typename vertex_t> struct result_t
{
    vertex_t *distances;
    vertex_t *predecessors;

    result_t(vertex_t *_distances, vertex_t *_predecessors) : distances(_distances), predecessors(_predecessors)
    {
    }
};

template <typename graph_t, typename param_type, typename result_type> struct problem_t : gunrock::problem_t<graph_t>
{
    param_type param;
    result_type result;

    problem_t(graph_t &G, param_type &_param, result_type &_result, std::shared_ptr<gcuda::multi_context_t> _context)
        : gunrock::problem_t<graph_t>(G, _context), param(_param), result(_result)
    {
    }

    using vertex_t = typename graph_t::vertex_type;
    using edge_t = typename graph_t::edge_type;
    using weight_t = typename graph_t::weight_type;

    thrust::device_vector<vertex_t> visited;

    void init() override
    {
    }

    void reset() override
    {
        auto d_predecessors = thrust::device_pointer_cast(this->result.predecessors);
        auto n_vertices = this->get_graph().get_number_of_vertices();
        auto d_distances = thrust::device_pointer_cast(this->result.distances);
        thrust::fill(thrust::device, d_predecessors, d_predecessors + n_vertices, -1);
        thrust::fill(thrust::device, d_distances + 0, d_distances + n_vertices, std::numeric_limits<vertex_t>::max());
        for (size_t i = 0; i < this->param.sources.size(); ++i)
        {
            vertex_t s = this->param.sources[i];
            thrust::fill(thrust::device, d_predecessors + s, d_predecessors + s + 1, s);
            thrust::fill(thrust::device, d_distances + s, d_distances + s + 1, 0);
        }
    }
};

template <typename problem_t> struct enactor_t : gunrock::enactor_t<problem_t>
{
    enactor_t(problem_t *_problem, std::shared_ptr<gcuda::multi_context_t> _context)
        : gunrock::enactor_t<problem_t>(_problem, _context)
    {
    }

    using vertex_t = typename problem_t::vertex_t;
    using edge_t = typename problem_t::edge_t;
    using weight_t = typename problem_t::weight_t;
    using frontier_t = typename enactor_t<problem_t>::frontier_t;

    void prepare_frontier(frontier_t *f, gcuda::multi_context_t &context) override
    {
        auto P = this->get_problem();
        for (size_t i = 0; i < P->param.sources.size(); ++i)
        {
            f->push_back(P->param.sources[i]);
        }
    }

    void loop(gcuda::multi_context_t &context) override
    {
        auto E = this->get_enactor();
        auto P = this->get_problem();
        auto G = P->get_graph();

        auto sources = P->param.sources;
        auto distances = P->result.distances;
        auto visited = P->visited.data().get();
        auto predecessors = P->result.predecessors;

        auto iteration = this->iteration;

        auto search = [distances, sources, iteration, predecessors] __host__ __device__(
                          vertex_t const &source, vertex_t const &neighbor, edge_t const &edge,
                          weight_t const &weight) -> bool {
            auto old_distance = math::atomic::min(&distances[neighbor], iteration + 1);
            if (iteration + 1 < old_distance)
            {
                math::atomic::cas(&predecessors[neighbor], static_cast<vertex_t>(-1), source);
                return true;
            }
            return false;
        };

        operators::advance::execute<operators::load_balance_t::block_mapped>(G, E, search, context);
    }
};

template <typename graph_t>
float run(graph_t &G, std::vector<typename graph_t::vertex_type> &sources, typename graph_t::vertex_type *distances,
          typename graph_t::vertex_type *predecessors,
          std::shared_ptr<gcuda::multi_context_t> context =
              std::shared_ptr<gcuda::multi_context_t>(new gcuda::multi_context_t(0)))
{
    using vertex_t = typename graph_t::vertex_type;
    using param_type = param_t<vertex_t>;
    using result_type = result_t<vertex_t>;

    param_type param(sources);
    result_type result(distances, predecessors);

    using problem_type = problem_t<graph_t, param_type, result_type>;
    using enactor_type = enactor_t<problem_type>;

    problem_type problem(G, param, result, context);
    problem.init();
    problem.reset();

    enactor_type enactor(&problem, context);
    return enactor.enact();
}

} // namespace bfs
} // namespace gunrock